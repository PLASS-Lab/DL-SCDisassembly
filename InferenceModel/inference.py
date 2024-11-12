import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers


# Function to load and preprocess dataset based on window size
def load_data(window_size):
    file_path = f'file_path{window_size}.csv'
    df = pd.read_csv(file_path)
    df = df.dropna()
    df.drop(['context', 'label', 'type'], axis=1, inplace=True)

    # Encode the 'instr' column
    encoder = LabelEncoder()
    df['instruction'] = encoder.fit_transform(df['instruction'])

    # Count the occurrences of each label
    label_counts = df['instruction'].value_counts()

    labels_to_remove = label_counts[label_counts < 100].index

    # Remove rows with these labels
    df = df[~df['instruction'].isin(labels_to_remove)]

    # To get the mapping of label encoder
    label_mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))

    print(label_mapping)

    # Create a new instance of LabelEncoder
    new_encoder = LabelEncoder()
    df['instruction'] = new_encoder.fit_transform(df['instruction'])


    # To get the new mapping of label encoder
    new_label_mapping = dict(zip(new_encoder.classes_, new_encoder.transform(new_encoder.classes_)))

    print("New label mapping:", new_label_mapping)

    # Print the remaining labels
    remaining_labels = df['instruction'].unique()
    print("Remaining labels:", remaining_labels)

    # Separate target variable
    target = df['instruction']

    return df, target

# Function to adjust feature names based on window size
def adjust_feature_names(features, window_size):
    return [f'{feature}_{window_size}' if feature not in ['Power'] else feature for feature in features]

def prepare_data(df, features, target, time_steps=3):
    # Dropping the target variable from dataset
    df = df[features]

    # performe a normalization preporcessing on all the features
    scaler = MinMaxScaler()
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    # Add 'Instruction' column back
    df['instruction'] = target.values

    # Prepare the dataset in the format, samples, time steps, features
    time_steps = 1
    data = []

    for i in range(len(df) - time_steps):
        data.append(df.iloc[i: i + time_steps].values)

    data = np.array(data)

    # Split dataset into training and validation sets 80, 20
    train_data, test_data, train_target, test_target = train_test_split(
        data, df['instruction'].values[time_steps:], test_size=0.2, stratify=df['instruction'].values[time_steps:], random_state=42)

    return train_data, test_data, train_target, test_target

# Model creation functions for each model type
def gru_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.GRU(256, input_shape=input_shape, return_sequences=True),
        tf.keras.layers.GRU(128, return_sequences=True),
        tf.keras.layers.GRU(64),
        tf.keras.layers.Dense(1)
    ])
    optimizer = tf.keras.optimizers.Adam(clipvalue=1.0, learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    return model

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Normalization and Attention
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    res = x + inputs

    # Feed Forward Part
    x = layers.LayerNormalization(epsilon=1e-6)(res)
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    return x + res

def transformer_model(input_shape):
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs

    # the number of encoders
    x = transformer_encoder(x, head_size=64, num_heads=4, ff_dim=256)
    x = transformer_encoder(x, head_size=64, num_heads=4, ff_dim=128)
    x = transformer_encoder(x, head_size=64, num_heads=4, ff_dim=64)

    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(1, activation="linear")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(loss="mean_squared_error", optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))

    return model

def adjust_predictions(predictions, actual_values):
    max_actual = actual_values.max()
    min_actual = actual_values.min()
    adjusted_predictions = np.clip(predictions, min_actual, max_actual)
    return adjusted_predictions

def test_all_options():
    all_results = []
    window_sizes = ['5', '10', '15', '20', '25', '30',  '35', '40', '45', '50']
    base_feature_sets = [
        ['Power'],
        ['Power', 'ewma', 'autocorrelation'],
        ['Power', 'MLTI_autocor', 'MLTI_EWMA']
        ['Power', 'ewma', 'autocorrelation', 'MLTI_autocor', 'MLTI_EWMA']
        # Other feature sets can be tested here
    ]

    for window_size in window_sizes:
        df, target = load_data(window_size)

        for base_features in base_feature_sets:
            features = adjust_feature_names(base_features, window_size)
            print(f"Running for window size {window_size} with features: {features}")

            train_data, test_data, train_target, test_target = prepare_data(df, features, target)

            models = {
                'Transformer': transformer_model((1, len(features) + 1)),
                'GRU': gru_model((1, len(features) + 1)),
            }

            train_data, test_data, train_target, test_target = prepare_data(df, features, target)
            for model_name, model in models.items():
            # Fit the model
                history = model.fit(train_data, train_target, epochs=100, batch_size=1024, verbose=1)

                print(test_data)

                # Prediction
                raw_predictions = model.predict(test_data).flatten()

                predictions = adjust_predictions(raw_predictions, test_target)
                predictions = np.round(predictions)

                # Save the predictions and actual values to a CSV file
                results_df = pd.DataFrame({'Actual': test_target, 'Predicted': predictions})
                feature_str = '_'.join(features)
                results_csv_file = f'{model_name}_prediction_{feature_str}_{window_size}.csv'
                results_df.to_csv(results_csv_file, index=False)
                print(f"Predictions saved to {results_csv_file}")


test_all_options()