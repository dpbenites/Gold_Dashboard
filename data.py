
import pandas as pd

class GoldData:
    def __init__(self, file_gold_production, file_gold_price, start_year, end_year, n_top_producers):
        self.df_gold = pd.read_csv(file_gold_production)
        self.df_gold.rename(columns={'Gold Production (Clio-Infra & USGS)': 'Gold Production'}, inplace=True)
        self.df_price = pd.read_csv(file_gold_price)
        self.df_price['Date'] = pd.to_datetime(self.df_price['Date'])
        self.start_year = start_year
        self.end_year = end_year
        self.n_top_producers = n_top_producers

    def ranking(self):
        df_filtered = self.df_gold[(self.df_gold['Year'] >= self.start_year) & (self.df_gold['Year'] <= self.end_year)]
        df_grouped = df_filtered.groupby('Entity')['Gold Production'].sum().reset_index()
        df_grouped.rename(columns={'Gold Production': 'Total Gold Production'}, inplace=True)
        df_ranked = df_grouped.sort_values(by='Total Gold Production', ascending=False).reset_index(drop=True)
        df_ranked = df_ranked.iloc[:self.n_top_producers + 1]

        total_top_countries = df_ranked.loc[1:, 'Total Gold Production'].sum()
        rest_of_world_production = df_ranked.loc[0, 'Total Gold Production'] - total_top_countries
        rest_of_world_df = pd.DataFrame({'Entity': ['Rest of World'], 'Total Gold Production': [rest_of_world_production]})
        df_ranked = pd.concat([df_ranked, rest_of_world_df], ignore_index=True)

        return df_ranked

    def gold_hist(self):
        top_countries = self.ranking()['Entity'].tolist()
        top_countries.pop(0)
        top_countries.pop(-1)

        df_filtered = self.df_gold[self.df_gold['Entity'].isin(top_countries)]
        df_filtered = df_filtered[(self.df_gold['Year'] >= self.start_year) & (self.df_gold['Year'] <= self.end_year)]
        return df_filtered

# Uso da classe GoldData
gold_data = GoldData('gold-production.csv', 'Gold_price.csv', 1920, 2010, 10)

# Exemplo de obtenção do ranking dos maiores produtores de ouro
top_producers = gold_data.ranking()
print(top_producers)

# Exemplo de filtragem de dados de produção de ouro
filtered_data = gold_data.gold_hist()
print(filtered_data)

        









