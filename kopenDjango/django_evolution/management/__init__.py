try:
    import cPickle as pickle
except ImportError:
    import pickle as pickle

from django.core.management.color import color_style
from django.db.models import signals, get_apps, get_app

from kopenDjango.django_evolution import is_multi_db, models as django_evolution
from kopenDjango.django_evolution.evolve import get_evolution_sequence, get_unapplied_evolutions
from kopenDjango.django_evolution.signature import create_project_sig
from kopenDjango.django_evolution.diff import Diff

style = color_style()


def install_baseline(app, latest_version, using_args, verbosity):
    app_label = app.__name__.split('.')[-2]
    sequence = get_evolution_sequence(app)

    if sequence:
        if verbosity > 0:
            print 'Evolutions in %s baseline:' % app_label, \
                  ', '.join(sequence)

    for evo_label in sequence:
        evolution = django_evolution.Evolution(app_label=app_label,
                                               label=evo_label,
                                               version=latest_version)
        evolution.save(**using_args)


def evolution(app, created_models, verbosity=1, **kwargs):
    """
    A hook into syncdb's post_syncdb signal, that is used to notify the user
    if a model evolution is necessary.
    """
    default_db = None
    if is_multi_db():
        from django.db.utils import DEFAULT_DB_ALIAS
        default_db = DEFAULT_DB_ALIAS

    db = kwargs.get('db', default_db)
    proj_sig = create_project_sig(db)
    signature = pickle.dumps(proj_sig)

    using_args = {}

    if is_multi_db():
        using_args['using'] = db

    try:
        if is_multi_db():
            latest_version = \
                django_evolution.Version.objects.using(db).latest('when')
        else:
            latest_version = django_evolution.Version.objects.latest('when')
    except django_evolution.Version.DoesNotExist:
        # We need to create a baseline version.
        if verbosity > 0:
            print "Installing baseline version"

        latest_version = django_evolution.Version(signature=signature)
        latest_version.save(**using_args)

        for a in get_apps():
            install_baseline(a, latest_version, using_args, verbosity)

    unapplied = get_unapplied_evolutions(app, db)

    if unapplied:
        print style.NOTICE('There are unapplied evolutions for %s.'
                           % app.__name__.split('.')[-2])

    # Evolutions are checked over the entire project, so we only need to check
    # once. We do this check when Django Evolutions itself is synchronized.
    if app == django_evolution:
        old_proj_sig = pickle.loads(str(latest_version.signature))

        # If any models or apps have been added, a baseline must be set
        # for those new models
        changed = False
        new_apps = []

        for app_name, new_app_sig in proj_sig.items():
            if app_name == '__version__':
                # Ignore the __version__ tag
                continue

            old_app_sig = old_proj_sig.get(app_name, None)

            if old_app_sig is None:
                # App has been added
                old_proj_sig[app_name] = proj_sig[app_name]
                new_apps.append(app_name)
                changed = True
            else:
                for model_name, new_model_sig in new_app_sig.items():
                    old_model_sig = old_app_sig.get(model_name, None)

                    if old_model_sig is None:
                        # Model has been added
                        old_proj_sig[app_name][model_name] = \
                            proj_sig[app_name][model_name]
                        changed = True

        if changed:
            if verbosity > 0:
                print "Adding baseline version for new models"

            latest_version = \
                django_evolution.Version(signature=pickle.dumps(old_proj_sig))
            latest_version.save(**using_args)

            for app_name in new_apps:
                app = get_app(app_name, True)

                if app:
                    install_baseline(app, latest_version, using_args, verbosity)

        # # If the current database state doesn't match the last
        # # saved signature (as reported by latest_version),
        # # then we need to update the Evolution table.
        # actual_sig = introspect_project_sig()
        # acutal = pickle.dumps(actual_sig)
        # if actual != latest_version.signature:
        #     nudge = Version(signature=actual)
        #     nudge.save()
        #     latest_version = nudge

        diff = Diff(old_proj_sig, proj_sig)

        if not diff.is_empty():
            print style.NOTICE(
                'Project signature has changed - an evolution is required')

            if verbosity > 1:
                old_proj_sig = pickle.loads(str(latest_version.signature))
                print diff

signals.post_syncdb.connect(evolution)
