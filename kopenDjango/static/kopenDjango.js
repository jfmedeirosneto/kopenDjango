// http://refresh-sf.com/yui/

// http://www.jshint.com/

// Versao dos estaticos (.js, .css)
function getStaticVersion() {
	var staticVersion = 100;
	return staticVersion;
}

// Desabilita Toolbar do Mobile Web Browser
function hideAddressBar() {
	if (!window.location.hash) {
		if (document.height < window.outerHeight) {
			document.body.style.height = (window.outerHeight + 50) + 'px';
		}
		setTimeout(function() {
			window.scrollTo(0, 1);
		}, 50);
	}
}
window.addEventListener("load", function() {
	if (!window.pageYOffset) {
		hideAddressBar();
	}
});
window.addEventListener("orientationchange", hideAddressBar); 

// DOM is ready (jQuery)
$(document).ready(function() {
	//jQuery Variables
	window.kopenHome = $("#home");
	window.kopenHomeUrl = $("meta[property='kopen:home']").attr("content");
	window.kopenDlgOferta = $("#id_dialog_ajax_oferta");
	window.conteudoOferta = window.kopenDlgOferta.find("#id_conteudo_oferta");
	window.kopenUrlAjaxOferta = window.kopenDlgOferta.attr("ajax_oferta");
	window.kopenPanelMenu = window.kopenHome.find("#id_panel_menu");
	window.kopenDlgInfo = $("#id_dialog_info");
	window.kopenDlgInfoContent = window.kopenDlgInfo.find("#id_dialog_info_content");
});

// Evento de inicializacao do jQuery Mobile
$(window.document).bind("mobileinit", function() {
	//jQuery Mobile customizations
	$.mobile.defaultDialogTransition = "none";
	$.mobile.defaultPageTransition = "none";
	$.mobile.buttonMarkup.hoverDelay = 0;
	$.mobile.loader.prototype.options.text = "Carregando...";
	$.mobile.loader.prototype.options.textVisible = true;
	$.mobile.loader.prototype.options.theme = "a";
	$.mobile.loader.prototype.options.html = "";
	$.mobile.pageLoadErrorMessage = "Erro ao carregar página.";
	$.mobile.pageLoadErrorMessageTheme = "a";
});

// WebView Back button (chamado pelo webview)
function webViewOnBackKeyDown() {
    if ($.mobile.activePage.attr("id") === "home") {
    	//Verifica menu
        if( ($("#id_panel_menu").css("visibility") === "hidden")        &&
            ($("#id_cidade1-listbox-screen").css("display") === "none") ) {
			window.webView.exit();
        } else {
        	$("#id_cidade1").selectmenu("close");
        	$("#id_panel_menu").panel("close");
        }
    } else {
		window.webView.back();    	
    }
};

// WebView Menu button (chamado pelo webview)
function webViewOnMenuKeyDown() {
	$("#id_cidade1").selectmenu("close");
	$("#id_panel_menu").panel("toggle");
};

// Funcoes para manipulacao dos cookies
function setCookie(name, value, days) {
	var expires = "";
	if (days) {
		var date = new Date();
		date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
		expires = "; expires=" + date.toGMTString();
	}
	document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(";");
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) === " ") {
			c = c.substring(1, c.length);
		}
		if (c.indexOf(nameEQ) === 0) {
			return c.substring(nameEQ.length, c.length);
		}
	}
	return null;
}

function deleteCookie(name) {
	setCookie(name, "", -1);
}

function deleteAllCookies() {
	var ca = document.cookie.split(";");
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) === " ") {
			c = c.substring(1, c.length);
		}		
		var entry = c.split("=");
		var name = entry[0];
		setCookie(name, "", -1);
	}
}

// Funcoes auxiliares
function getTime() {
	var time = new Date();
	return time.getTime();
}

function isNumberKey(evt) {
	var charCode = (evt.which) ? evt.which : event.keyCode;
	if (charCode !== 44 && charCode > 31 && (charCode < 48 || charCode > 57)) {
		return false;
	}
	return true;
}

function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Funcao JQuery Ajax Padrao para kopenDjango
function kopenDefaultAjax(url, data, type, successFunction, showLoader, showError, errorFunction) {
	if (showLoader === undefined) showLoader = true;
	if (showError === undefined) showError = true;
	$.ajax({
		url : url,
		data : data,
		type : type,
		dataType : "json",
		contentType : "application/x-www-form-urlencoded",
		cache : false,
		timeout : 15000,
		crossDomain : false, // obviates need for sameOrigin test
		beforeSend : function(xhr, settings) {
			if (showLoader) {
				$.mobile.loading("show");
			}
			xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			xhr.setRequestHeader("Cache-Control", "no-cache");
			if (!csrfSafeMethod(settings.type)) {
				xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
			}
		},
		success : function(data, textStatus, jqXHR) {
			if (showLoader) {
				$.mobile.loading("hide");
			}
			successFunction(data);
		},
		error : function(jqXHR, textStatus, errorThrown) {
			if (showLoader) {
				$.mobile.loading("hide");
			}
			if (errorFunction) {
				errorFunction();
			}						
			if (showError) {
				if (jqXHR.status === 0) {
					alert("Sem conexão de rede ou servidor inacessível.\n" + errorThrown);
				} else if (jqXHR.status === 404) {
					alert("Página não existe no servidor [404].\n" + errorThrown);
				} else if (jqXHR.status === 500) {
					alert("Erro interno do servidor [500].\n" + errorThrown);
				} else if (textStatus === "parsererror") {
					alert("Tratamento da solicitação JSON falhou.\n" + errorThrown);
				} else if (textStatus === "timeout") {
					alert("Tempo da comunicação excedido [Timeout].\n" + errorThrown);
				} else if (textStatus === "abort") {
					alert("Solicitação Ajax abortada." + errorThrown);
				} else {
					alert("Erro desconhecido.\n" + jqXHR.responseText);
				}
			}
		},
		complete : function(jqXHR, textStatus) {
			if (showLoader) {
				$.mobile.loading("hide");
			}
		}
	});
}

//Funcao para ir para a pagina home (jQuery Mobile)
function kopenMobileGoHome() {
	$.mobile.changePage(window.kopenHome);
}

//Funcao para ir para a pagina home (window.location.href)
function kopenGoHome() {
	window.location.href = window.kopenHomeUrl;
}

//Funcao para abrir o dialog de info e fechar apos o timeout
function kopenOpenInfo(text, closeFunction) {
	window.kopenDlgInfoContent.html(text);
	$.mobile.changePage(window.kopenDlgInfo, {
		transition : "none"
	});
	setTimeout(function() {
		if (closeFunction) {
			closeFunction();
		} else {
			window.kopenDlgInfo.dialog("close");
		}
	}, 2000);
}

//Funcao default para submissao de formulario
function kopenDefaultFormSubmit(formError, formSubmit, sucessText, successFunction, errorFunction, ajaxErrorFunction) {
	formError.hide();
	var url = formSubmit.attr("action");
	var data = formSubmit.serialize();
	kopenDefaultAjax( url, data, "POST", function(json) {
		var response_json = json;
		if (json.status) {
			kopenOpenInfo(sucessText, function() {
				if( successFunction ) {
					successFunction(response_json);
				}
			});
		} else {
			formError.text(json.message).show();
			$.mobile.silentScroll(formError.offset().top);
			if( errorFunction ) {
				errorFunction(response_json);
			}
		}
	}, true, true, ajaxErrorFunction);
}

//Funcao para carregar oferta via Ajax
function kopenOpenOferta(json) {
	if (json.status) {
		//Conteudo da oferta
		window.conteudoOferta.html(json.message);

		//Inicializa controles
		var btLikes = window.kopenDlgOferta.find("#id_botao_like,#id_botao_dislike");
		var btShares = window.kopenDlgOferta.find("#id_botao_facebook,#id_botao_twitter,#id_botao_google_plus");
		var btNavs = window.kopenDlgOferta.find("#id_botao_previous,#id_botao_next");
		var btSearches = window.kopenDlgOferta.find("#id_link_local_oferta");
		var divLike1 = window.kopenDlgOferta.find("#id_div_like");
		var divDislike1 = window.kopenDlgOferta.find("#id_div_dislike");
		divLike1.badger(json.liked);
		divDislike1.badger(json.disliked);
		window.kopenDlgOferta.find("#id_botao_report").button();

		//Botoes gostou e nao gostou
		btLikes.button().click(function(event) {
			//Verifica se ja opinou para essa oferta
			var btn = $(this);
			var cookieName = btn.attr("cookie");
			if (getCookie(cookieName) === null) {
				var plink = btn.attr("href").split("?");
				var url = plink[0];
				var data = plink[1];
				kopenDefaultAjax(url, data, "POST", function(json) {
					if (json.status) {
						setCookie(cookieName, "True", 7);
						divLike1.badger(json.liked);
						divDislike1.badger(json.disliked);
					} else {
						alert(json.message);
					}
				});
			} else {
				alert("Desculpe, mas você já opinou nessa oferta!");
			}
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();
			return false;
		});

		//Botoes de compartilhar
		btShares.button().click(function(event) {
			var btn = $(this);
			var href = btn.attr("href");
			var plink = btn.attr("callback").split("?");
			var url = plink[0];
			var data = plink[1];
			kopenDefaultAjax(url, data, "POST", function(json) {
				if (json.status) {
					window.open(href, "_self", "location=no");
				} else {
					alert(json.message);
				}
			});
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();
			return false;			
		});

		//Botoes anterior e proximo
		btNavs.button().click(function(event) {
			//Simula click de oferta
			var oferta = $(this).attr("oferta");
			$(oferta).trigger("click");
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();
			return false;
		});
		
		//Botoes search
		btSearches.button().click(function(event) {
			var btn = $(this);
			var href = btn.attr("href");
			var plink = btn.attr("callback").split("?");
			var url = plink[0];
			var data = plink[1];
			kopenDefaultAjax(url, data, "POST", function(json) {
				if (json.status) {
					window.open(href, "_self", "location=no");
				
				} else {
					alert(json.message);
				}
			});
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();
			return false;						
		});			
		
		//Botao outras ofertas
		window.kopenDlgOferta.find("#id_botao_go_home").button().click(function(event) {
			//Link outras ofertas
			var btn = $(this);
			var plink = btn.attr("href").split("?busca=");
			var url = plink[0];
			var busca = plink[1];
			//Ao voltar para o home
			function showHome(event) {
				//Desabilita evento
				$(window.document).off("pageshow", "#home", showHome);
				//Transfere para busca
				var formBusca = window.kopenHome.find("#id_form_busca");
				formBusca.find("#id_busca").val(busca.split("+").join("\u0020"));
				//Submete busca
				formBusca.submit();				
			}
			$(window.document).on("pageshow", "#home", showHome);
			//Go Home
			kopenMobileGoHome();
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();
			return false;
		});
		
		//Chama dialog
		$.mobile.changePage(window.kopenDlgOferta, {
			transition : "none",
			role : "dialog"
		});
	} else {
		alert(json.message);
	}
}

// Ao inicializar dialogo de login
$(window.document).on("pageinit", "#id_dialog_login", function(event) {
	//Clicou no botao para fechar
	var dlgLogin = $("#id_dialog_login");
	dlgLogin.find(".ui-icon-delete").click(kopenGoHome);
	
	//Submissao do formulario de login
	var formLogin = dlgLogin.find("#id_form_login");
	formLogin.submit(function(event) {
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(dlgLogin.find("#id_form_error1"), formLogin, "Você entrou com sucesso.", function() {
			$("#id_dialog_login").dialog("close");
			kopenGoHome();
		});
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
	
	//Botao entrar pelo facebook
	dlgLogin.find("#id_facebook_login").click(function(event) {
		var btn = $(this);
		var href = btn.attr("href");
		$.mobile.loading("show");
		window.open(href, "_self", "location=no");
		$.mobile.loading("hide");
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;		
	});	
});

// Ao mostrar dialogo de login
$(window.document).on("pageshow", "#id_dialog_login", function(event) {
	//Inicializacao dos controles
	var dlgLogin = $("#id_dialog_login");
	dlgLogin.find("#id_user1").val("").focus();
	dlgLogin.find("#id_password1").val("");
	dlgLogin.find("#id_form_error1").hide();
});

// Ao inicializar dialogo de solicitar senha
$(window.document).on("pageinit", "#id_dialog_request_password", function(event) {
	//Submissao do formulario de solicitar senha
	var dlgRequest = $("#id_dialog_request_password");
	var formRequest = dlgRequest.find("#id_form_request_password");
	formRequest.submit(function(event) {
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(dlgRequest.find("#id_form_error6"), formRequest, "Senha enviada com sucesso para seu email.", kopenMobileGoHome);
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
});

// Ao mostrar dialogo de solicitar senha
$(window.document).on("pageshow", "#id_dialog_request_password", function(event) {
	//Inicializacao dos controles
	var dlgRequest = $("#id_dialog_request_password");
	dlgRequest.find("#id_email2").val("").focus();
	dlgRequest.find("#id_form_error6").hide();
});

// Ao abrir menu
$(window.document).on("panelopen", "#id_panel_menu", function(event) {
	//Botao Logout
	var btnLogout = window.kopenPanelMenu.find("#id_button_logout");
	btnLogout.click(function(event) {
		var url = btnLogout.attr("href");
		var data = btnLogout.serialize();
		kopenDefaultAjax(url, data, "GET", function(json) {
			//Open Info
			kopenOpenInfo(json.message, function() {
				//Delete cookies desse documento
				deleteAllCookies();
				//Acoes para WebView
				if( window.webView ) {
					//Remove todos os cookies do WebView
					window.webView.removeAllCookies();
					//Sair do WebView
					window.webView.exit();
				} else {
					//Vai para pagina principal
					kopenGoHome();					
				}
			});
		});
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
});

// Ao inicializar dialogo de registro
$(window.document).on("pageinit", "#id_dialog_register_user", function(event) {
	//Clicou no botao para fechar
	var dlgRegister = $("#id_dialog_register_user");
	dlgRegister.find(".ui-icon-delete").click(kopenGoHome);

	//Se leu os termos de uso
	var btnReadLicense = dlgRegister.find("#id_read_license");
	btnReadLicense.click(function(event) {
		var val1 = dlgRegister.find("#id_user2").val();
		var val2 = dlgRegister.find("#id_name2").val();
		var val3 = dlgRegister.find("#id_email2").val();
		var val4 = dlgRegister.find("#id_password2").val();
		//Ao voltar para o dialogo de registro
		function showDialogRegister(event) {
			//Desabilita evento
			$(window.document).off("pageshow", "#id_dialog_register_user", showDialogRegister);
			//Habilita checkbox dos termos de uso
			var dlgRegister = $("#id_dialog_register_user");
			dlgRegister.find("#id_license2").prop("disabled", false).checkboxradio("refresh");
			//Volta valores digitados anteriormente
			dlgRegister.find("#id_user2").val(val1);
			dlgRegister.find("#id_name2").val(val2);
			dlgRegister.find("#id_email2").val(val3);
			dlgRegister.find("#id_password2").val(val4);
		}
		$(window.document).on("pageshow", "#id_dialog_register_user", showDialogRegister);
		//Vai para o dialogo de termos de uso
		$.mobile.changePage(btnReadLicense.attr("href"));
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});

	//Submissao do formulario de registro
	var formRegister = dlgRegister.find("#id_form_register");
	formRegister.submit(function(event) {
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		//Tratamento formulario
		var formError2 = dlgRegister.find("#id_form_error2");
		var readLicense2 = dlgRegister.find("#id_license2");
		formError2.hide();
		//Se ainda nao leu a licensa
		if (readLicense2.prop("disabled")) {
			alert("Primeiro leia os Termos de Uso.");
			//do not follow the link
			return false;
		}
		//Se nao aceitou a licensa
		if (readLicense2.prop("checked") === false) {
			alert("Você deve concordar com os Termos de Uso.");
			//do not follow the link
			return false;
		}
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(formError2, formRegister, "Novo usuário registrado com sucesso.", function() {
			$("#id_dialog_register_user").dialog("close");
			kopenGoHome();
		});
		//do not follow the link
		return false;
	});

	//Botao Registrar pelo Facebook
	dlgRegister.find("#id_facebook_register").click(function(event) {
		//Tratamento formulario
		var readLicense2 = dlgRegister.find("#id_license2");
		//Se ainda nao leu a licensa
		if (readLicense2.prop("disabled")) {
			alert("Primeiro leia os Termos de Uso.");
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();			
			return false;
		}
		//Se nao aceitou a licensa
		if (readLicense2.prop("checked") === false) {
			alert("Você deve concordar com os Termos de Uso.");
			//do not follow the link
			event.stopPropagation();
			event.preventDefault();			
			return false;
		}
		//Abre outra janela
		var btn = $(this);
		var href = btn.attr("href");
		$.mobile.loading("show");
		window.open(href, "_self", "location=no");
		$.mobile.loading("hide");
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;		
	});
});

// Ao mostrar dialogo de registro
$(window.document).on("pageshow", "#id_dialog_register_user", function(event) {
	//Inicializacao dos controles
	var dlgRegister = $("#id_dialog_register_user");
	dlgRegister.find("#id_user2").val("").focus();
	dlgRegister.find("#id_name2").val("");
	dlgRegister.find("#id_email2").val("");
	dlgRegister.find("#id_password2").val("");
	dlgRegister.find("#id_form_error2").hide();
	dlgRegister.find("#id_license2").prop("disabled", true);
});

// Ao inicializar dialogo de dados do usuario
$(window.document).on("pageinit", "#id_dialog_change_user", function(event) {
	//Submissao do formulario de alteracao dados do usuario
	var dlgChangeUser = $("#id_dialog_change_user");
	var formChangeUser = dlgChangeUser.find("#id_form_user");
	formChangeUser.submit(function(event) {
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(dlgChangeUser.find("#id_form_error3"), formChangeUser, "Dados alterados com sucesso.", kopenMobileGoHome);
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
	
	//Botao conectar ao facebook
	dlgChangeUser.find("#id_facebook_connect").click(function(event) {
		var btn = $(this);
		var href = btn.attr("href");
		$.mobile.loading("show");
		window.open(href, "_self", "location=no");
		$.mobile.loading("hide");
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;		
	});	
});

// Ao mostrar dialogo de dados do usuario
$(window.document).on("pageshow", "#id_dialog_change_user", function(event) {
	//Inicializacao dos controles
	var dlgChangeUser = $("#id_dialog_change_user");
	dlgChangeUser.find("#id_form_error3").hide();
});

// Ao inicializar dialogo de recuper senha
$(window.document).on("pageinit", "#id_dialog_change_password", function(event) {
	//Submissao do formulario de recuperar senha
	var dlgChangePassword = $("#id_dialog_change_password");
	var formChangePassword = dlgChangePassword.find("#id_form_user");
	formChangePassword.submit(function(event) {
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(dlgChangePassword.find("#id_form_error8"), formChangePassword, "Senha alterada com sucesso.", kopenGoHome);
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
});

// Ao mostrar dialogo de recuper senha
$(window.document).on("pageshow", "#id_dialog_change_password", function(event) {
	//Inicializacao dos controles
	var dlgChangePassword = $("#id_dialog_change_password");
	dlgChangePassword.find("#id_form_error8").hide();
	dlgChangePassword.find("#id_password8").focus();
});

// Ao inicializar pagina home (principal)
$(window.document).on("pageinit", "#home", function(event) {
	//Link dos destaques da pagina principal
	window.kopenHome.find("a[id^=id_link_destaque]").click(function(event) {
		var originalUrl = $(this).attr("href");
		var n = originalUrl.indexOf("?id=");
		var data = originalUrl.substring(n + 1);
		kopenDefaultAjax(window.kopenUrlAjaxOferta, data, "GET", kopenOpenOferta);
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});

	//Autocomplete da busca
	var formBusca = window.kopenHome.find("#id_form_busca");
	var buscaProdutos = formBusca.find("#id_busca_produtos");
	var buscaProdutosList = buscaProdutos.find("#id_busca_produtos_list");
	var inputBusca = formBusca.find("#id_busca");	
	inputBusca.on("input", function(event) {
		var text = inputBusca.val();
		if (text.length < 3) {
			buscaProdutos.hide();
		} else {
			var url = inputBusca.attr("ajax_produtos");
			var cidade = formBusca.find("#id_cidade1").val();
			kopenDefaultAjax(url, { "busca": text, "cidade": cidade, "ativos": 1 }, "GET", function(json) {
				if( json.length > 0 ) {
					//Monta lista de sugeridos
					var str = "";
					for (var i = 0, len = json.length; i < len; i++) {
						str += "<li id=\"id_busca_item_" + i + "\" >" + json[i] + "</li>";
					}
					
					//Habilita sugeridos
					buscaProdutosList.html(str);
					var newtop = buscaProdutos.height() + 7;
					buscaProdutos.css("top", "-" + newtop + "px").show();
					
					//Desabilita apos 4 segundos
					if( window.timeOut1 ) {
						window.clearTimeout(window.timeOut1);
					}
					window.timeOut1 = setTimeout("$('#id_busca_produtos').hide();", 4000);					
										
					//Clicado em algum item da lista
					buscaProdutosList.find("li[id^=id_busca_item]").click(function(event) {
						//Transfere para busca
						inputBusca.val($(this).text());
						//Submete busca
						formBusca.submit();						
						//Desativa sugeridos
						setTimeout("$('#id_busca_produtos').hide();", 300);
						//do not follow the link
						event.stopPropagation();
						event.preventDefault();
						return false;
					});
				} else {
					buscaProdutos.hide();
				}
			}, false, false);
		}
	});

	//Submissao do formulario de pesquisa de produtos
	var formErrorBusca = window.kopenHome.find("#id_form_error_busca");
	var conteudoBusca = window.kopenHome.find("#id_conteudo_busca");
	var groupOrdenar = formBusca.find("#id_group_ordenar");
	formBusca.submit(function(event) {
		formErrorBusca.hide();
		conteudoBusca.hide();
		groupOrdenar.hide();
		var url = formBusca.attr("action");
		var data = formBusca.serialize();
		kopenDefaultAjax(url, data, "POST", function(json) {
			if (json.status) {
				//Lista de ofertas
				conteudoBusca.html(json.message);
				conteudoBusca.find("#id_ofertas_listview").listview();
				conteudoBusca.show();
				groupOrdenar.show();
				$.mobile.silentScroll(conteudoBusca.offset().top);
				//Link de ofertas que vieram na lista
				conteudoBusca.find("a[id^=id_link_oferta]").click(function(event) {
					formErrorBusca.hide();
					var originalUrl = $(this).attr("href");
					var n = originalUrl.indexOf("?id=");
					var data = originalUrl.substring(n + 1);
					kopenDefaultAjax(window.kopenUrlAjaxOferta, data, "GET", kopenOpenOferta);
					//do not follow the link
					event.stopPropagation();
					event.preventDefault();
					return false;
				});
				
				//Botoes para compartilhar busca
				conteudoBusca.find("#id_botao_facebook,#id_botao_twitter,#id_botao_google_plus").button().click(function(event) {
					var btn = $(this);
					var href = btn.attr("href");
					var plink = btn.attr("callback").split("?");
					var url = plink[0];
					var data = plink[1];
					kopenDefaultAjax(url, data, "POST", function(json) {
						if (json.status) {
							window.open(href, "_self", "location=no");
						} else {
							alert(json.message);
						}
					});
					//do not follow the link
					event.stopPropagation();
					event.preventDefault();
					return false;		
				});
			} else {
				formErrorBusca.text(json.message).show();
			}
		});
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});

	//Radio para mudar a ordenacao da busca
	groupOrdenar.find("input[id^=id_ordenar]").click(function() {
		//Submete formulario de busca
		formBusca.submit();
	});
});

// Ao mostrar dialogo ver oferta
$(window.document).on("pageshow", "#id_dialog_oferta", function(event) {
	//Inicializa controles
	var dlgVerOferta = $("#id_dialog_oferta");
	var divLike2 = dlgVerOferta.find("#id_div_like");
	var divDislike2 = dlgVerOferta.find("#id_div_dislike");
	divLike2.badger(divLike2.attr("liked"));
	divDislike2.badger(divDislike2.attr("disliked"));

	//Botoes gostou e nao gostou
	dlgVerOferta.find("#id_botao_like,#id_botao_dislike").click(function(event) {
		//Verifica se ja opinou para essa oferta
		var btn = $(this);
		var cookieName = btn.attr("cookie");
		if (getCookie(cookieName) === null) {
			var plink = btn.attr("href").split("?");
			var url = plink[0];
			var data = plink[1];
			kopenDefaultAjax(url, data, "POST", function(json) {
				if (json.status) {
					setCookie(cookieName, "True", 7);
					divLike2.badger(json.liked);
					divDislike2.badger(json.disliked);
				} else {
					alert(json.message);
				}
			});
		} else {
			alert("Desculpe, mas você já opinou nessa oferta!");
		}
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});

	//Botoes de compartilhar
	dlgVerOferta.find("#id_botao_facebook,#id_botao_twitter,#id_botao_google_plus").click(function(event) {
		var btn = $(this);
		var href = btn.attr("href");
		var plink = btn.attr("callback").split("?");
		var url = plink[0];
		var data = plink[1];
		kopenDefaultAjax(url, data, "POST", function(json) {
			if (json.status) {
				window.open(href, "_self", "location=no");
			} else {
				alert(json.message);
			}
		});
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;		
	});
	
	//Botoes search local oferta
	dlgVerOferta.find("#id_link_local_oferta").button().click(function(event) {
		var btn = $(this);
		var href = btn.attr("href");
		var plink = btn.attr("callback").split("?");
		var url = plink[0];
		var data = plink[1];
		kopenDefaultAjax(url, data, "POST", function(json) {
			if (json.status) {
				window.open(href, "_self", "location=no");
			} else {
				alert(json.message);
			}
		});
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;						
	});	
});

// Ao inicializar dialogo de adicionar oferta
$(window.document).on("pageinit", "#id_dialog_add_oferta", function(event) {
	//Autocomplete do produto
	var dlgAddOferta = $("#id_dialog_add_oferta");
	var formAddOferta = dlgAddOferta.find("#id_form_add_oferta");
	var buscaProdutos = formAddOferta.find("#id_busca_produtos_add");
	var buscaProdutosList = buscaProdutos.find("#id_busca_produtos_add_list");
	var inputProduto = formAddOferta.find("#id_produto");
	inputProduto.on("input", function(event) {
		var text = inputProduto.val();
		if (text.length < 3) {
			buscaProdutos.hide();
		} else {
			var url = inputProduto.attr("ajax_produtos");
			var cidade = formAddOferta.find("#id_cidade2").val();
			kopenDefaultAjax(url, { "busca": text, "cidade": cidade, "ativos": 0 }, "GET", function(json) {
				if( json.length > 0 ) {
					//Monta lista de sugeridos
					var str = "";
					for (var i = 0, len = json.length; i < len; i++) {
						str += "<li id=\"id_produto_item_" + i + "\" >" + json[i] + "</li>";
					}
					
					//Habilita sugeridos
					buscaProdutosList.html(str);
					var newtop = buscaProdutos.height() + 7;
					buscaProdutos.css("top", "-" + newtop + "px").show();
					
					//Desabilita apos 4 segundos
					if( window.timeOut2 ) {
						window.clearTimeout(window.timeOut2);
					}
					window.timeOut2 = setTimeout("$('#id_busca_produtos_add').hide();", 4000);					
						
					//Clicado em algum item da lista
					buscaProdutosList.find("li[id^=id_produto_item_]").click(function(event) {
						//Transfere para produto
						inputProduto.val($(this).text());
						//Desativa sugeridos
						setTimeout("$('#id_busca_produtos_add').hide();", 300);
						//do not follow the link
						event.stopPropagation();
						event.preventDefault();
						return false;
					});
				} else {
					buscaProdutos.hide();
				}
			}, false, false);
		}
	});

	//Autocomplete dos locais
	var buscaLocais = formAddOferta.find("#id_busca_locais_add");
	var buscaLocaisList = buscaLocais.find("#id_busca_locais_add_list");
	var inputLocal = formAddOferta.find("#id_local");
	inputLocal.on("input", function(event) {
		var text = inputLocal.val();
		if (text.length < 3) {
			buscaLocais.hide();
		} else {
			var url = inputLocal.attr("ajax_locais");
			kopenDefaultAjax(url, { "busca" : text }, "GET", function(json) {
				if( json.length > 0 ) {
					//Monta lista de sugeridos
					var str = "";
					for (var i = 0, len = json.length; i < len; i++) {
						str += "<li id=\"id_local_item_" + i + "\" >" + json[i] + "</li>";
					}
					
					//Habilita sugeridos
					buscaLocaisList.html(str);
					var newtop = buscaLocais.height() + 7;
					buscaLocais.css("top", "-" + newtop + "px").show();
					
					//Desabilita apos 5 segundos
					if( window.timeOut3 ) {
						window.clearTimeout(window.timeOut3);
					}
					window.timeOut3 = setTimeout("$('#id_busca_locais_add').hide();", 4000);
						
					//Clicado em algum item da lista
					buscaLocais.find("li[id^=id_local_item_]").click(function(event) {
						//Transfere para local
						inputLocal.val($(this).text());
						//Desativa sugeridos
						setTimeout("$('#id_busca_locais_add').hide();", 300);
						//do not follow the link
						event.stopPropagation();
						event.preventDefault();
						return false;
					});
				} else {
					buscaLocais.hide();
				}
			}, false, false);
		}
	});

	//Submissao do formulario de adicionar oferta
	formAddOferta.submit(function(event) {
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		
		//Desabilitar submit do fomulario
		var buttonSubmit = $(this).find(":submit");
		var oldSubmitText = buttonSubmit.prop("value");
		buttonSubmit.prop("value", "Aguarde...").button("disable").button("refresh");
		
		//Habilita submit do formulario
		function enableSubmitButton() {
			//Habilitar botao de submit
			buttonSubmit.prop("value", oldSubmitText).button("enable").button("refresh");							
		}		
		
		//Limpa erro
		var formError = dlgAddOferta.find("#id_form_error5");
		formError.hide();
		
		//Verifica produto
		var text = inputProduto.val();
		var url = inputProduto.attr("ajax_check_produto");
		kopenDefaultAjax(url, { "produto" : text }, "GET", function(json) {
			//Verifica se quer criar um novo produto
			if (json.status === false) {
				if (text.length >= 3) {
					var conf = confirm("Esse produto ainda não foi cadastrado.\nDeseja criar esse novo produto (OK) ou selecionar um existente (Cancelar)?");
					if (conf === false) {
						enableSubmitButton();
						//do not follow the link
						return false;
					}
				}
			}
			
			//Verifica local
			text = inputLocal.val();
			url = inputLocal.attr("ajax_check_local");
			kopenDefaultAjax(url, { "local" : text }, "GET", function(json) {
				//Verifica se quer criar um novo local
				if (json.status === false) {
					if (text.length >= 3) {
						var conf = confirm("Esse local ainda não foi cadastrado.\nDeseja criar esse novo local (OK) ou selecionar um existente (Cancelar)?");
						if (conf === false) {
							enableSubmitButton();							
							//do not follow the link
							return false;
						}
					}
				}
				
				//Funcao para submeter formulario
				kopenDefaultFormSubmit(formError, formAddOferta, "Obrigado! Oferta cadastrada com sucesso.", function(json) {
					//Id da oferta adicionada
					var oferta_id = json.oferta_id;
					//Ao voltar para o home
					function showHome(event) {
						//Desabilita evento
						$(window.document).off("pageshow", "#home", showHome);
						//Carrega ajax da oferta
						var data = "id=" + oferta_id;
						kopenDefaultAjax(window.kopenUrlAjaxOferta, data, "GET", kopenOpenOferta);
					}
					$(window.document).on("pageshow", "#home", showHome);
					//Go Home
					kopenMobileGoHome();
				}, enableSubmitButton, enableSubmitButton);			
			}, true, true, enableSubmitButton);			
		}, true, true, enableSubmitButton);
		
		//do not follow the link
		return false;
	});
});

// Ao mostrar dialogo de adicionar oferta
$(window.document).on("pageshow", "#id_dialog_add_oferta", function(event) {
	//Inicializacao dos controles
	var dlgAddOferta = $("#id_dialog_add_oferta");
	dlgAddOferta.find("#id_produto").val("").focus();
	dlgAddOferta.find("#id_busca_produtos_add").hide();
	dlgAddOferta.find("#id_local").val("");
	dlgAddOferta.find("#id_busca_locais_add").hide();
	dlgAddOferta.find("#id_preco").val("");
	dlgAddOferta.find("#id_form_error5").hide();
});

// Ao inicializar dialogo de informar problema de oferta
$(window.document).on("pageinit", "#id_dialog_report_oferta", function(event) {
	//Botoes report oferta
	var dlgReportOferta = $("#id_dialog_report_oferta");
	dlgReportOferta.find("a[id^=id_botao_report_erro]").click(function(event) {
		var formError7 = dlgReportOferta.find("#id_form_error7");
		formError7.hide();
		//Verifica se ja informou sobre essa oferta
		var btn = $(this);
		var cookieName = btn.attr("cookie");
		if (getCookie(cookieName) === null) {
			var plink = btn.attr("href").split("?");
			var url = plink[0];
			var data = plink[1];
			kopenDefaultAjax(url, data, "POST", function(json) {
				if (json.status) {
					var closeFunction = function(event) {
						$(window.document).off("pagebeforeshow", "#id_dialog_report_oferta", closeFunction);
						//Refresh das variaveis
						var dlgReportOferta = $("#id_dialog_report_oferta");
						dlgReportOferta.dialog("close");
					};
					$(window.document).on("pagebeforeshow", "#id_dialog_report_oferta", closeFunction);
					kopenOpenInfo(json.message);
				} else {
					formError7.text(json.message).show();
					$.mobile.silentScroll(formError7.offset().top);
				}
				setCookie(cookieName, "True", 7);
			});
		} else {
			alert("Desculpe, mas você já informou erro sobre essa oferta!");
		}
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
});

// Ao mostrar dialogo de informar problema de oferta
$(window.document).on("pageshow", "#id_dialog_report_oferta", function(event) {
	//Inicializacao dos controles
	var dlgReportOferta = $("#id_dialog_report_oferta");
	dlgReportOferta.find("#id_form_error7").hide();
});

// Ao inicializar dialogo de fale conosco
$(window.document).on("pageinit", "#id_dialog_contact_form", function(event) {
	//Submissao do formulario de contato
	var dlgContactForm = $("#id_dialog_contact_form");
	var formContactForm = dlgContactForm.find("#id_form_contact_form");
	formContactForm.submit(function(event) {
		//Funcao para submeter formulario
		kopenDefaultFormSubmit(dlgContactForm.find("#id_form_error10"), formContactForm, "Obrigado! Mensagem enviada com sucesso.<br/>Responderemos assim que possível.", kopenMobileGoHome);
		//do not follow the link
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
});

// Ao mostrar dialogo de fale conosco
$(window.document).on("pageshow", "#id_dialog_contact_form", function(event) {
	//Inicializacao dos controles
	var dlgContactForm = $("#id_dialog_contact_form");
	dlgContactForm.find("#id_form_error10").hide();
});

// Ao inicializar dialogo de termos de uso
$(window.document).on("pageinit", "#id_dialog_termos_uso", function(event) {
	//Clicou no botao para fechar
	var dlgTermos = $("#id_dialog_termos_uso");
	dlgTermos.find(".ui-icon-delete").click(kopenGoHome);
});