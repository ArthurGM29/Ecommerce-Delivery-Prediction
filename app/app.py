import streamlit as st
import pandas as pd
import joblib
import os

# Configuração da página
st.set_page_config(page_title="Alerta de Demurrage & SLA", page_icon="🚛", layout="centered")

st.title('🚛 Previsão de SLA e Risco Logístico')
st.markdown("Insira os dados da operação abaixo para que a nossa IA calcule o risco do pedido ser entregue com atraso.")

# Carregando o modelo salvo
# Usando caminho absoluto para evitar erros quando o Streamlit rodar
model_path = os.path.join(os.path.dirname(__file__), '../src/random_forest_model.pkl')

try:
    model = joblib.load(model_path)
except FileNotFoundError:
    st.error("Erro: O arquivo do modelo não foi encontrado. Certifique-se de ter rodado o treinamento.")
    st.stop()

# Layout em colunas pra ficar bonito
col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox('Mês do Pedido (Sazonalidade)', range(1, 13), help="1 = Jan, 12 = Dez")
    tempo_estimado = st.number_input('Dias Prometidos p/ Entrega', min_value=1, value=10)
    frete = st.number_input('Valor do Frete (R$)', min_value=0.0, value=25.0)
    peso = st.number_input('Peso do Produto (g)', min_value=100, max_value=50000, value=1000)

with col2:
    preco = st.number_input('Valor do Produto (R$)', min_value=1.0, value=150.0)
    dia_semana = st.selectbox('Dia da Compra', options=[0, 1, 2, 3, 4, 5, 6], format_func=lambda x: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][x])
    mesma_cidade = st.radio('Origem e Destino no mesmo Estado?', ['Sim', 'Não'])
    is_same_state_val = 1 if mesma_cidade == 'Sim' else 0

st.markdown("---")

# Botão de Ação
if st.button('Prever Risco de Atraso', use_container_width=True):
    
    # Criando o dataframe invisível com a mesma ordem que o modelo aprendeu
    input_data = pd.DataFrame([[preco, frete, peso, tempo_estimado, mes, dia_semana, is_same_state_val]], 
                              columns=['price', 'freight_value', 'product_weight_g', 'estimated_transit_time', 
                                       'order_month', 'order_day_of_week', 'is_same_state'])
    
    # A IA fazendo  previsão em tempo real
    prob_atraso = model.predict_proba(input_data)[0][1]
    
    # Exibindo o resultado com regras de negócio
    if prob_atraso >= 0.5:
        st.error(f"⚠️ ALTO RISCO DE ATRASO! Probabilidade: {prob_atraso * 100:.1f}%")
        st.warning("Recomendação: Intervenção manual na logística requerida. Sugerir troca de transportadora ou enviar alerta proativo ao cliente.")
    elif prob_atraso >= 0.3:
        st.warning(f"🟡 Atenção. Risco moderado: {prob_atraso * 100:.1f}%")
    else:
        st.success(f"✅ Operação Segura. Risco de apenas: {prob_atraso * 100:.1f}%. Pedido dentro do SLA.")