import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM, Conv1D, Flatten
from keras.optimizers import Adam
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, precision_score, recall_score, precision_score, recall_score, roc_auc_score, confusion_matrix, matthews_corrcoef
from sklearn.preprocessing import StandardScaler
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import os

def is_valid_input(selected_indices, max_index):
    # If user enters 'none' or leaves it empty, it's considered a valid input
    if not selected_indices or (len(selected_indices) == 1 and (selected_indices[0].lower() == 'none' or selected_indices[0].strip() == '')):
        return True

    for index in selected_indices:
        if not index.isdigit() or not (1 <= int(index) <= max_index):
            return False
    return True


def run_experiment(window_size, selected_features, features_list):
    input_dir = f'input_dir{window_size}.csv'
    df = pd.read_csv(input_dir)

    # Modify feature names based on selected window size
    selected_features = [f"{feature}_{window_size}" for feature in selected_features]

    # Columns to always drop
    columns_to_drop = ['type', 'context', 'instruction'] + [f"{feature}_{window_size}" for feature in features_list if f"{feature}_{window_size}" not in selected_features and feature != 'wavelet_transform']

    # Drop specified columns
    df = df.drop(columns_to_drop, axis=1)
    print(df.head(5))

    # Identify string columns and convert to categorical
    string_cols = df.select_dtypes(include=[object]).columns.tolist()
    le = LabelEncoder()
    for col in string_cols:
        df[col] = le.fit_transform(df[col])

    # Define features and labels
    X = df.drop(['label'], axis=1)
    y = df['label']

    print(df.columns)

    # Split the data (80:20 ratio)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # For feature matrix X:
    print("Number of rows in X_train:", X_train.shape[0])
    print("Number of rows in X_test:", X_test.shape[0])

    # For target vector y:
    print("Number of rows in y_train:", y_train.shape[0]) 
    print("Number of rows in y_test:", y_test.shape[0])   
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(X_test_scaled)

    # Reshape data for LSTM and Conv1D
    X_train_scaled_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
    X_test_scaled_reshaped = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))


    # Convert labels to one-hot encoding
    y_train_onehot = to_categorical(y_train)
    y_test_onehot = to_categorical(y_test)
    print(y_test_onehot)

    # Artificial Neural Network
    print("Training ANN...")
    ann = Sequential()
    ann.add(Dense(128, input_dim=X_train.shape[1], activation='relu'))
    ann.add(Dense(64, activation='relu'))
    ann.add(Dense(2, activation='softmax'))
    ann.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])
    ann.fit(X_train_scaled, y_train_onehot, epochs=10, batch_size=256)
    y_pred_onehot = ann.predict(X_test_scaled)
    y_pred = np.argmax(y_pred_onehot, axis=1)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_onehot[:, 1]) 
    conf_matrix = confusion_matrix(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print(f"ANN, Accuracy: {accuracy}, F1 score: {f1}, Precision: {precision}, Recall: {recall}, ROC-AUC: {roc_auc}, Confusion Matrix: \n{conf_matrix}, MCC: {mcc}")

    # LSTM
    print("Training LSTM...")
    lstm = Sequential()
    lstm.add(LSTM(50, input_shape=(X_train.shape[1], 1)))
    lstm.add(Dense(2, activation='softmax'))
    lstm.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])
    lstm.fit(X_train_scaled_reshaped, y_train_onehot, epochs=10, batch_size=256)
    y_pred_onehot = lstm.predict(X_test_scaled_reshaped)
    y_pred = np.argmax(y_pred_onehot, axis=1)
    lstm_precision = precision_score(y_test, y_pred)
    lstm_recall = recall_score(y_test, y_pred)
    lstm_roc_auc = roc_auc_score(y_test, y_pred_onehot[:, 1])
    lstm_conf_matrix = confusion_matrix(y_test, y_pred)
    lstm_mcc = matthews_corrcoef(y_test, y_pred)
    lstm_accuracy = accuracy_score(y_test, y_pred)
    lstm_f1 = f1_score(y_test, y_pred)
    print(f"LSTM, Accuracy: {accuracy}, F1 score: {f1}, Precision: {precision}, Recall: {recall}, ROC-AUC: {roc_auc}, Confusion Matrix: \n{conf_matrix}, MCC: {mcc}")

    # Conv1D
    print("Training Conv1D...")
    conv1d = Sequential()
    conv1d.add(Conv1D(filters=32, kernel_size=1, activation='relu', input_shape=(X_train.shape[1], 1)))
    conv1d.add(Flatten())
    conv1d.add(Dense(2, activation='softmax'))
    conv1d.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])
    conv1d.fit(X_train_scaled_reshaped, y_train_onehot, epochs=10, batch_size=256)
    y_pred_onehot = conv1d.predict(X_test_scaled_reshaped)
    y_pred = np.argmax(y_pred_onehot, axis=1)
    conv1d_precision = precision_score(y_test, y_pred)
    conv1d_recall = recall_score(y_test, y_pred)
    conv1d_roc_auc = roc_auc_score(y_test, y_pred_onehot[:, 1])
    conv1d_conf_matrix = confusion_matrix(y_test, y_pred)
    conv1d_mcc = matthews_corrcoef(y_test, y_pred)
    conv1d_accuracy = accuracy_score(y_test, y_pred)
    conv1d_f1 = f1_score(y_test, y_pred)
    print(f"Comv1D, Accuracy: {accuracy}, F1 score: {f1}, Precision: {precision}, Recall: {recall}, ROC-AUC: {roc_auc}, Confusion Matrix: \n{conf_matrix}, MCC: {mcc}")

    # Prepare a dictionary to store the results
    results = {
        "window_size": window_size,
        "features": ", ".join(selected_features),
        # ANN metrics
        "ANN_accuracy": accuracy,
        "ANN_f1_score": f1,
        "ANN_precision": precision,
        "ANN_recall": recall,
        "ANN_roc_auc": roc_auc,
        "ANN_conf_matrix": conf_matrix,
        "ANN_mcc": mcc,
        # LSTM metrics
        "LSTM_accuracy": lstm_accuracy,  
        "LSTM_f1_score": lstm_f1,  
        "LSTM_precision": lstm_precision,  
        "LSTM_recall": lstm_recall,  
        "LSTM_roc_auc": lstm_roc_auc,  
        "LSTM_conf_matrix": lstm_conf_matrix,  
        "LSTM_mcc": lstm_mcc,  
        # Conv1D metrics
        "Conv1D_accuracy": conv1d_accuracy,  
        "Conv1D_f1_score": conv1d_f1,  
        "Conv1D_precision": conv1d_precision,  
        "Conv1D_recall": conv1d_recall,  
        "Conv1D_roc_auc": conv1d_roc_auc,  
        "Conv1D_conf_matrix": conv1d_conf_matrix,  
        "Conv1D_mcc": conv1d_mcc,  
    }

        # Save Predictions and Actual Values
    def save_predictions(model_name, y_test, y_pred, features, window):
        filename = fr"{model_name}_predictions_{features}_window_{window}.csv"
        df_predictions = pd.DataFrame({
            'Actual': y_test,
            'Predicted': y_pred
        })
        df_predictions.to_csv(filename, index=False)

    # For each model, after making predictions, save them
    # ANN Predictions
    save_predictions('ANN', y_test, y_pred, '_'.join(selected_features), window_size)
    
    # LSTM Predictions
    y_pred_lstm = np.argmax(lstm.predict(X_test_scaled_reshaped), axis=1)
    save_predictions('LSTM', y_test, y_pred_lstm, '_'.join(selected_features), window_size)

    # Conv1D Predictions
    y_pred_conv1d = np.argmax(conv1d.predict(X_test_scaled_reshaped), axis=1)
    save_predictions('Conv1D', y_test, y_pred_conv1d, '_'.join(selected_features), window_size)

    return results

def test_all_options():
    all_results = []
    window_sizes = ['5', '10', '15', '20', '25', '30',  '35', '40', '45', '50']
    feature_sets = [
        ['autocorrelation', 'ewma'],
        ['MLTI_EWMA', 'MLTI_autocor'],
        ['autocorrelation', 'ewma', 'MLTI_EWMA', 'MLTI_autocor'],
    ]

    for window in window_sizes:
        for feature_set in feature_sets:
            result = run_experiment(window, feature_set, features_list)
            all_results.append(result)

    # Convert the results to a DataFrame and save as CSV
    df_results = pd.DataFrame(all_results)
    df_results.to_csv('experiment_results.csv', index=False)

# Ask the user if they want to test all options
test_all = input("Do you want to test all options? Enter 'yes' to test all, or 'no' to proceed with custom settings: ").strip().lower()

features_list = ['mean', 'std_dev', 'max', 'ewma', 'autocorrelation', 'MLTI_autocor', 
                 'MLTI_EWMA'] 

if test_all == 'yes':
    test_all_options()
else:
    window_size = input("Enter the window size (5, 10, or 15): ").strip()

    # Let the user select the features
    print("Select features from the following list:")
    for i, feature in enumerate(features_list, 1):
        print(f"{i}. {feature}")

    # Get a valid input from the user
    max_index = len(features_list)
    selected_indices = input("Enter the numbers of the features you want to use, separated by commas (e.g., 1,2,3), or leave empty to only use the power feature: ").split(',')

    while not is_valid_input(selected_indices, max_index):
        print("Invalid input. Please enter numbers from the list, 'none', or leave it empty.")
        selected_indices = input("Enter the numbers of the features you want to use, separated by commas (e.g., 1,2,3), or leave empty or type 'none' to select no optional features: ").split(',')

    # If 'none' or empty string was entered, there are no selected optional features
    if not selected_indices or (len(selected_indices) == 1 and (selected_indices[0].lower() == 'none' or selected_indices[0].strip() == '')):
        selected_features = []
    else:
        # Convert selected indices to selected features
        selected_features = [features_list[int(index) - 1] for index in selected_indices]

    run_experiment(window_size, selected_features, features_list)  # pass features_list

        # After getting selected_features and window_size
    result = run_experiment(window_size, selected_features, features_list)
    
    # Save the single result to a CSV
    df_result = pd.DataFrame([result])  
    df_result.to_csv('classification_result_v2.csv', index=False)
