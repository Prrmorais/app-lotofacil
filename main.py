import flet as ft
# Blocos de importação protegidos para evitar Tela Branca
try:
    import itertools
    import pandas as pd
    import os
    import sys
    import requests
    from collections import Counter
    MODULOS_OK = True
    ERRO_IMPORT = ""
except Exception as e:
    MODULOS_OK = False
    ERRO_IMPORT = str(e)

# Variável global
df_para_salvar = None

def main(page: ft.Page):
    global df_para_salvar
    
    page.title = "Debug Lotofácil"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- TELA DE ERRO (CASO FALHE IMPORTAÇÃO) ---
    if not MODULOS_OK:
        page.add(
            ft.Column([
                ft.Icon(ft.icons.ERROR, color="red", size=50),
                ft.Text("ERRO CRÍTICO NA INICIALIZAÇÃO", color="red", weight="bold"),
                ft.Text(f"O App não conseguiu carregar uma biblioteca.\nErro: {ERRO_IMPORT}", color="black"),
                ft.Text("Verifique o arquivo requirements.txt no GitHub.", color="grey")
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        return

    # --- SE O CÓDIGO CHEGOU AQUI, AS BIBLIOTECAS ESTÃO OK ---

    lbl_status = ft.Text("Pronto.", color="grey", weight="bold")
    lista_resultados = ft.ListView(expand=1, spacing=10, padding=20)

    # Componentes de UI
    txt_concurso_alvo = ft.TextField(label="Próximo", width=130, text_align="center")
    txt_concurso_base = ft.TextField(label="Último", width=130, text_align="center")
    chk_usar_online = ft.Checkbox(label="Online", value=True)

    # --- FUNÇÃO DE SALVAMENTO ---
    def salvar_arquivo_final(e: ft.FilePickerResultEvent):
        try:
            if e.path:
                df_para_salvar.to_csv(e.path, index=False, sep=';', encoding='utf-8-sig')
                lbl_status.value = "Arquivo Salvo com Sucesso!"
                lbl_status.color = "green"
                page.update()
        except Exception as ex:
            lbl_status.value = f"Erro ao salvar: {ex}"
            page.update()

    file_picker = ft.FilePicker(on_result=salvar_arquivo_final)
    page.overlay.append(file_picker)

    # --- LÓGICA SIMPLIFICADA PARA TESTE ---
    def gerar_jogos(e):
        global df_para_salvar
        lbl_status.value = "Processando..."
        page.update()

        try:
            # Teste de Conexão (Simples)
            origem = "Offline"
            pool = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20} # Padrão
            
            if chk_usar_online.value:
                try:
                    r = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/3000", timeout=5)
                    if r.status_code == 200:
                        origem = "Online OK"
                except Exception as ex_net:
                    origem = f"Erro Net: {ex_net}"

            # Geração de 1 jogo teste
            dados = [{"Teste": "Funcionou", "Origem": origem, "Dezenas": "01;02;03;04;05..."}]
            
            # Cards
            lista_resultados.controls.clear()
            lista_resultados.controls.append(
                ft.Container(
                    content=ft.Text(f"Teste Concluído!\nStatus Net: {origem}", color="white"),
                    bgcolor="green", padding=10, border_radius=10
                )
            )
            
            # Preparar Salvamento
            df_para_salvar = pd.DataFrame(dados)
            file_picker.save_file(file_name="teste_loto.csv", allowed_extensions=["csv"])
            
        except Exception as erro_geral:
            lbl_status.value = f"Erro na lógica: {erro_geral}"
            lbl_status.color = "red"
        
        page.update()

    # Botão Sair Seguro
    def fechar(e):
        page.window_close()

    btn_gerar = ft.FilledButton("TESTAR APP", on_click=gerar_jogos)
    btn_sair = ft.FilledButton("SAIR", on_click=fechar, style=ft.ButtonStyle(bgcolor="red"))

    page.add(
        ft.Column([
            ft.Text("Modo de Recuperação", size=20, weight="bold"),
            ft.Row([txt_concurso_alvo, txt_concurso_base], alignment="center"),
            chk_usar_online,
            ft.Row([btn_sair, btn_gerar], alignment="center"),
            lbl_status,
            lista_resultados
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)
