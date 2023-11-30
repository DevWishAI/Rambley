import torch
import math
import os
import PySimpleGUI as sg

# Parâmetros de Rambley
peso_coeficiente = 0.3333  # Aqui Você Pode Ajustar De Acordo Com Preços De Locais De Reciclagem.
taxa_fixa = 0.0

# Caminho do modelo
modelo_caminho = "Rambley.pth"

# Modelo Rambley
class RambleyModel(torch.nn.Module):
    def __init__(self):
        super(RambleyModel, self).__init__()
        self.peso_coef = torch.nn.Parameter(torch.tensor(peso_coeficiente))
        self.taxa_fixa = torch.nn.Parameter(torch.tensor(taxa_fixa))

    def forward(self, peso):
        return peso * self.peso_coef + self.taxa_fixa

# Função para calcular o preço
def calcular_preco(peso, model):
    return model(peso).item()

# Função para criar a janela de configuração
def create_config_window(model):
    config_layout = [
        [sg.Text('Configurações', font=('Helvetica', 14), justification='c')],
        [sg.Text('Novo Peso Coeficiente:'), sg.InputText(key='novo_coef', size=(10, 1))],
        [sg.Text('Nova Taxa Fixa:'), sg.InputText(key='nova_taxa', size=(10, 1))],
        [sg.Button('Salvar')]
    ]

    return sg.Window('Configurações Rambley', config_layout, background_color='#36393F',
                     element_justification='c', auto_size_text=True, finalize=True)

# Verifica se o modelo já existe
if os.path.exists(modelo_caminho):
    # Carrega o modelo
    model = torch.load(modelo_caminho)
    print("Rambley carregado.")
else:
    # Cria um novo modelo
    model = RambleyModel()
    print("Rambley criado.")

# Layout da interface
layout = [
    [sg.Text('Insira o KG para Rambley saber:', text_color='white')],
    [sg.InputText(key='input', size=(10, 1)), sg.Text('', size=(None, None), key='output', text_color='white')],
    [sg.Button('Enviar'), sg.Button('Config'), sg.Button('Encerrar')]
]

# Cria a janela com o layout
window = sg.Window('Rambley!', layout, background_color='#36393F',
                   element_justification='c', auto_size_text=True, finalize=True)

config_window = None

# Loop da interface
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Encerrar':
        print("Tchau!")

        # Salva o modelo antes de encerrar
        torch.save(model, modelo_caminho)
        print("Rambley salvo.")
        break

    elif event == 'Enviar':
        try:
            # Obtém o peso do input
            peso_objeto = float(values['input'].replace(',', '.'))

            # Verifica se o usuário deseja encerrar
            if peso_objeto == 0:
                print("Tchau!")

                # Salva o modelo antes de encerrar
                torch.save(model, modelo_caminho)
                print("Rambley salvo.")
                break

            # Cálculo do preço estimado usando a função calcular_preco
            preco_calculado = calcular_preco(peso_objeto, model)

            # Atualiza o texto na interface
            window['output'].update(f"Rambley: Opa! Rambley Aqui, O Preço Estimado é de {preco_calculado:.2f} Reais.")

        except ValueError:
            sg.popup_error('Por favor, insira um valor numérico válido.')

    elif event == 'Config':
        # Store the current state of the main window before opening the configuration window
        prev_main_window_state = window.CurrentLocation()

        # Abre a janela de configuração
        config_window = create_config_window(model)

    # Verifica eventos na janela de configuração
    if config_window:
        config_event, config_values = config_window.read()

        if config_event == sg.WINDOW_CLOSED:
            config_window.close()
            config_window = None

            # Restore the main window to its previous state
            window.Move(prev_main_window_state[0], prev_main_window_state[1])

        elif config_event == 'Salvar':
            try:
                # Atualiza os parâmetros com os novos valores
                novo_coeficiente = float(config_values['novo_coef'].replace(',', '.'))
                nova_taxa = float(config_values['nova_taxa'].replace(',', '.'))

                # Cria um novo modelo com os parâmetros atualizados
                new_model = RambleyModel()
                new_model.peso_coef.data = torch.tensor(novo_coeficiente)
                new_model.taxa_fixa.data = torch.tensor(nova_taxa)

                # Atualiza o modelo atual com os novos parâmetros
                model.peso_coef.data = new_model.peso_coef.data
                model.taxa_fixa.data = new_model.taxa_fixa.data

                print("Configurações atualizadas!")

            except ValueError:
                sg.popup_error('Por favor, insira valores numéricos válidos nas configurações.')

# Fecha a janela principal ao encerrar
window.close()

