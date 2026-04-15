# E-commerce SLA Prediction: Previsão de Risco Logístico e Atrasos

## 1. Visão Executiva e Problema de Negócio
No varejo digital, a quebra de SLA de Entrega (Atrasos) é um dos maiores ofensores de rentabilidade. Cada pedido atrasado gera custos diretos com tickets de suporte e reembolsos, além do impacto indireto no LTV (Lifetime Value) devido à péssima experiência do cliente.

O objetivo deste projeto End-to-End foi desenvolver uma solução preditiva para estimar a probabilidade de atraso de um pedido no momento do faturamento. Atuando como uma ponte entre a engenharia de dados e a Diretoria de Operações, o modelo permite que a equipe de logística atue de forma prescritiva — trocando a transportadora em tempo real ou enviando um aviso antecipado ao cliente — mitigando o impacto na operação.

---

## 2. Arquitetura da Solução e Stack Tecnológico
O projeto foi estruturado seguindo as melhores práticas de Engenharia de Software aplicadas à Ciência de Dados (modularização, ambientes virtuais isolados e versionamento semântico).

* Fonte de Dados: Dataset público do E-commerce brasileiro (Olist) disponível no Kaggle. Foram utilizados 5 arquivos específicos para a modelagem:
  * `olist_orders_dataset.csv` (Tabela Fato)
  * `olist_customers_dataset.csv` (Dimensão de Clientes)
  * `olist_order_items_dataset.csv` (Itens do Pedido/Preço/Frete)
  * `olist_products_dataset.csv` (Dimensão de Produtos)
  * `olist_sellers_dataset.csv` (Dimensão de Vendedores)
* SGBD (Simulação de Data Warehouse): SQLite.
* Processamento e pipeline de ETL: SQL (Extração relacional) e Python/Pandas (Transformação).
* Advanced Analytics & ML: Scikit-Learn (Random Forest Classifier).
* Deploy e Front-end: Streamlit.
* Versionamento: Git/GitHub.

---

## 3. Engenharia de Dados (Pipeline ETL)
A base bruta desnormalizada foi injetada em um banco de dados relacional para simular um ambiente corporativo. A extração foi feita via scripts SQL, realizando os devidos JOINs entre as tabelas de Fato (Pedidos) e Dimensões (Clientes, Produtos, Vendedores, Itens).

### Script de Extração SQL
```sql
SELECT 
    o.order_id,
    o.order_purchase_timestamp AS order_date,
    o.order_estimated_delivery_date AS promised_delivery_date,
    o.order_delivered_customer_date AS actual_delivery_date,
    c.customer_state,
    i.price,
    i.freight_value,
    p.product_weight_g,
    s.seller_state
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items i ON o.order_id = i.order_id
JOIN products p ON i.product_id = p.product_id
JOIN sellers s ON i.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
```
Transformação e Feature Engineering (Pandas)

Apliquei técnicas para traduzir colunas temporais e geográficas em variáveis matemáticas de negócio:
``` # Cálculo da variável alvo e novas features
df['is_late'] = (df['actual_delivery_date'] > df['promised_delivery_date']).astype(int)
df['estimated_transit_time'] = (df['promised_delivery_date'] - df['order_date']).dt.days
df['order_month'] = df['order_date'].dt.month
df['is_same_state'] = (df['customer_state'] == df['seller_state']).astype(int)
```

## 4. Modelagem Preditiva (Machine Learning)
O problema foi modelado como uma Classificação Binária. Como os atrasos representam a minoria da base histórica (~7.9%), utilizei o hiperparâmetro class_weight='balanced' para lidar com o desbalanceamento das classes.

Treinamento do Modelo:
```from sklearn.ensemble import RandomForestClassifier```

# Configuração do modelo com foco em explicabilidade e tratamento de desbalanceamento:
```
model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    random_state=42, 
    class_weight='balanced'
)

model.fit(X_train, y_train)
```

Avaliação de Performance:
Atingimos um ROC-AUC de 0.763. 
O modelo demonstrou alta capacidade de separação estatística, garantindo um nível de confiança sólido para a operação acionar o plano de contingência antes da quebra do SLA.

## 5. Business Insights (O Raio-X da Operação)
A análise de Feature Importance revelou as causas raiz dos atrasos:

Gargalo Sazonal (order_month): Os atrasos estão concentrados em picos de volumetria (Black Friday e Natal), indicando falta de elasticidade na malha logística atual.

Falha de Precificação de Prazo (estimated_transit_time): Prazos calculados de forma muito agressiva pelo motor de frete geram quebras sistêmicas inevitáveis.

O Mito da Carga Pesada: O peso do produto impacta menos a taxa de atraso do que a sazonalidade e o custo do frete, corrigindo um viés operacional comum da empresa.

## 6. Deploy: O Produto Final em Produção
Para democratizar o acesso à IA, desenvolvi um Web App interativo em Streamlit. A interface permite que analistas de logística simulem o risco de um pedido em tempo real.

Lógica do Dashboard (app.py):
```
import streamlit as st
import joblib

model = joblib.load('src/random_forest_model.pkl')

if st.button('Prever Risco de Atraso'):
    prob_atraso = model.predict_proba(input_data)[0][1]
    if prob_atraso >= 0.5:
        st.error(f"ALTO RISCO DE ATRASO! Probabilidade: {prob_atraso * 100:.1f}%")
```

## 7. Reproducibilidade (Como Executar Localmente)
Clone o repositório:
```
git clone https://github.com/ArthurGM29/Ecommerce-Delivery-Prediction.git
cd Ecommerce-Delivery-Prediction
```

Configure o ambiente virtual e instale as dependências:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Execute o aplicativo:
```
streamlit run app/app.py
```

## Contato

| 👨‍💻 Autor | **Arthur Mesquita** |
| :--- | :--- |
| **Cargo** | Analista de Dados & BI |
| **LinkedIn** | [linkedin.com/in/arthur-g-mesquita](https://www.linkedin.com/in/arthur-g-mesquita) |
| **Localização** | 📍 Recife, PE |