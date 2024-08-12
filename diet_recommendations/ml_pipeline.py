import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

print('Hello world')

def ml_model(food_df, nutrients_metrics):
   
    # only selecting the relevant columns
    relevant_cols = ['Name','CookTime','PrepTime','TotalTime','RecipeIngredientParts','Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent','RecipeInstructions', 'Images']
    food_df = food_df[relevant_cols]

    # print(food_df)

    max_Calories=2000
    max_daily_fat=100
    max_daily_Saturatedfat=13
    max_daily_Cholesterol=300
    max_daily_Sodium=2300
    max_daily_Carbohydrate=325
    max_daily_Fiber=40
    max_daily_Sugar=40
    max_daily_Protein=200
    max_list=[max_Calories,max_daily_fat,max_daily_Saturatedfat,max_daily_Cholesterol,max_daily_Sodium,max_daily_Carbohydrate,max_daily_Fiber,max_daily_Sugar,max_daily_Protein]


    extracted_data = food_df.copy()
    columns_to_bo_filtered = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
    for column, maximum in zip(columns_to_bo_filtered, max_list):
        print(f'Column is: {column} and maximum values is: {maximum}')
    extracted_data=extracted_data[extracted_data[column] <= maximum]


    target = ['Name']
    features = list(extracted_data.columns[5:14])


    print(len(extracted_data))
    # Generate a heat map from this...
    # extracted_data.iloc[:,5:14].corr()

    # Data preprocessing
    scaler = StandardScaler()
    data_to_transform = extracted_data.iloc[:, 5:14].to_numpy()
    scaled_data = scaler.fit_transform(data_to_transform)

    print(scaled_data.shape)

    from sklearn.neighbors import NearestNeighbors
    # Nearest Neighbors model
    nn_model = NearestNeighbors(metric='manhattan', algorithm='brute')
    nn_model.fit(scaled_data)

    # FunctionTransformer and Pipeline
    params = {'n_neighbors': 5, 'return_distance': False}
    transformer = FunctionTransformer(nn_model.kneighbors, kw_args=params)
    pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])

    sample_data = np.array([nutrients_metrics])

    try:
        # Testing the model
        transformed_sample = pipeline.transform(sample_data)
        nearest_neighbor_indices = transformed_sample[0]
        nearest_neighbor_data = extracted_data.iloc[nearest_neighbor_indices]
        return nearest_neighbor_data[relevant_cols]
    except Exception as e:
        return f"Error during transformation: {e}"