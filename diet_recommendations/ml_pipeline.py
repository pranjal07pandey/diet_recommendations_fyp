import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer



print('Hello world')

def ml_model(food_df, nutrients_metrics):

    # Suppress all UserWarnings
    # warnings.filterwarnings("ignore", category=UserWarning)
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
    
    # Trying out Faiss algorithm
    # Now let's create a matrix for FAISS
    # numerical_features = ['Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent']

    # dataset_filtered = extracted_data.copy()
    # scaler = StandardScaler()
    # data_to_transform = extracted_data.iloc[:, 5:14].to_numpy()
    # dataset_filtered[numerical_features] = scaler.fit_transform(data_to_transform)

    # import faiss
    # features_matrix = dataset_filtered[numerical_features].values.astype('float32')

    # # Step 1: Create the FAISS index
    # d = features_matrix.shape[1]  # dimension of features
    # nlist = 100  # Number of clusters (for IVF)
    # quantizer = faiss.IndexFlatL2(d)  # the quantizer
    # index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

    # # Step 2: Train the index
    # index.train(features_matrix)

    # # Step 3: Add vectors to the index
    # index.add(features_matrix)

    # # Step 4: Make the index searchable
    # index.nprobe = 10  # number of clusters to search in

    # # Step 1: Define the user's input
    # # user_input = [500, 20, 10, 150, 1200, 500, 20, 10, 40]  # Example input
    # user_input_faiss = np.array(nutrients_metrics).reshape(1, -1).astype('float32')

    # print(user_input_faiss)
    # # Step 2: Scale the user's input using the same scaler
    # scaler.fit(dataset_filtered[numerical_features])
    # print("done fitting")
    # # user_input_scaled_faiss = scaler.transform(user_input_faiss)
    # print("done scaling")
    # # Step 3: Search for the most similar foods using FAISS
    # distances_faiss, indices_faiss = index.search(user_input_faiss, 5)  # Search for top 5 similar foods
    
    # print(distances_faiss, indices_faiss)
    # original_dataset_recommendations_with_nutirents = extracted_data.iloc[indices_faiss[0]][relevant_cols]

    # return original_dataset_recommendations_with_nutirents