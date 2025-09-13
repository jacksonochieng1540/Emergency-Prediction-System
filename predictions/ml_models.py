import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import json
import os
from django.conf import settings

class EmergencyPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.label_encoder = None
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            model_dir = settings.ML_MODELS_PATH
            self.models['random_forest'] = joblib.load(os.path.join(model_dir, 'random_forest.pkl'))
            self.models['gradient_boosting'] = joblib.load(os.path.join(model_dir, 'gradient_boosting.pkl'))
            self.scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
            self.label_encoder = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))
            print("Models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
            self.models = {}
    
    def train_models(self, data_path=None):
        """Train ML models on emergency data"""
        if data_path is None:
            data_path = os.path.join(settings.BASE_DIR, 'ml_models', 'training_data', 'emergency_data.csv')
        
        # Load data
        df = pd.read_csv(data_path)
        
        # Preprocess data
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.month
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df = df.drop('timestamp', axis=1)
        
        # Encode emergency type
        le = LabelEncoder()
        df['emergency_type_encoded'] = le.fit_transform(df['emergency_type'])
        
        # Define features and target
        X = df.drop(['emergency_type', 'emergency_type_encoded', 'emergency_probability'], axis=1)
        y = df['emergency_type_encoded']
        
        # Handle missing values
        imputer = SimpleImputer(strategy='mean')
        X = imputer.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        # Define models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'svm': SVC(probability=True, random_state=42)
        }
        
        # Train and evaluate models
        results = {}
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'report': classification_report(y_test, y_pred, output_dict=True)
            }
            print(f"{name} accuracy: {accuracy:.4f}")
        
        # Save best model and preprocessing objects
        best_model_name = max(results.items(), key=lambda x: x[1]['accuracy'])[0]
        best_model = results[best_model_name]['model']
        
        model_dir = settings.ML_MODELS_PATH
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(best_model, os.path.join(model_dir, f'{best_model_name}.pkl'))
        joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
        joblib.dump(le, os.path.join(model_dir, 'label_encoder.pkl'))
        
        # Save results
        with open(os.path.join(model_dir, 'training_results.json'), 'w') as f:
            json_results = {name: {'accuracy': res['accuracy']} for name, res in results.items()}
            json.dump(json_results, f, indent=2)
        
        print(f"Best model: {best_model_name} with accuracy {results[best_model_name]['accuracy']:.4f}")
        return results
    
    def predict(self, features):
        """Predict emergency type based on input features"""
        if not self.models or 'random_forest' not in self.models:
            raise ValueError("Models not loaded. Please train or load models first.")
        
        # Convert features to numpy array
        feature_array = np.array(features).reshape(1, -1)
        
        # Scale features
        scaled_features = self.scaler.transform(feature_array)
        
        # Make prediction
        model = self.models['random_forest']
        prediction = model.predict(scaled_features)
        probabilities = model.predict_proba(scaled_features)
        
        # Decode prediction
        emergency_type = self.label_encoder.inverse_transform(prediction)[0]
        confidence = probabilities[0][prediction[0]]
        
        return emergency_type, confidence, probabilities[0]
    
    def get_severity(self, emergency_type, confidence):
        """Determine severity based on emergency type and confidence"""
        severity_map = {
            'none': 'none',
            'medical': 'low' if confidence < 0.7 else 'medium',
            'accident': 'medium' if confidence < 0.7 else 'high',
            'fire': 'high' if confidence < 0.8 else 'critical',
            'natural_disaster': 'critical'
        }
        return severity_map.get(emergency_type, 'none')