import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import json
import os

class DataPreprocessingService:
    @staticmethod
    def read_dataset(file_path, file_type):
        """读取数据集文件"""
        if file_type == 'csv':
            return pd.read_csv(file_path)
        elif file_type == 'excel':
            return pd.read_excel(file_path)
        elif file_type == 'json':
            return pd.read_json(file_path)
        raise ValueError(f"不支持的文件类型: {file_type}")

    @staticmethod
    def get_dataset_info(df):
        """获取数据集信息"""
        return {
            'columns': [
                {
                    'name': col,
                    'type': str(df[col].dtype),
                    'missing': int(df[col].isnull().sum()),
                    'unique': int(df[col].nunique())
                }
                for col in df.columns
            ],
            'row_count': len(df)
        }

    @staticmethod
    def clean_data(df, parameters):
        """数据清洗"""
        # 处理缺失值
        if parameters.get('handle_missing'):
            strategy = parameters.get('missing_strategy', 'mean')
            for col in df.select_dtypes(include=[np.number]).columns:
                if strategy == 'mean':
                    df[col].fillna(df[col].mean(), inplace=True)
                elif strategy == 'median':
                    df[col].fillna(df[col].median(), inplace=True)
                elif strategy == 'mode':
                    df[col].fillna(df[col].mode()[0], inplace=True)
            
            # 对非数值列使用众数填充
            for col in df.select_dtypes(exclude=[np.number]).columns:
                df[col].fillna(df[col].mode()[0], inplace=True)

        # 删除重复行
        if parameters.get('remove_duplicates'):
            df.drop_duplicates(inplace=True)

        # 删除指定列
        if columns_to_drop := parameters.get('columns_to_drop'):
            df.drop(columns=columns_to_drop, inplace=True)

        return df

    @staticmethod
    def transform_data(df, parameters):
        """数据转换"""
        transformations = parameters.get('transformations', [])
        
        for transform in transformations:
            col = transform['column']
            operation = transform['operation']
            
            if operation == 'log':
                df[f'{col}_log'] = np.log1p(df[col])
            elif operation == 'sqrt':
                df[f'{col}_sqrt'] = np.sqrt(df[col])
            elif operation == 'square':
                df[f'{col}_squared'] = df[col] ** 2
            elif operation == 'zscore':
                df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()
            elif operation == 'minmax':
                df[f'{col}_scaled'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        return df

    @staticmethod
    def encode_data(df, parameters):
        """编码转换"""
        encoding_config = parameters.get('encoding', [])
        encoders = {}
        
        for config in encoding_config:
            col = config['column']
            method = config['method']
            
            if method == 'label':
                encoder = LabelEncoder()
                df[f'{col}_encoded'] = encoder.fit_transform(df[col])
                encoders[col] = encoder
            elif method == 'onehot':
                df = pd.get_dummies(df, columns=[col], prefix=col)
            elif method == 'ordinal':
                mapping = config.get('mapping', {})
                df[f'{col}_encoded'] = df[col].map(mapping)

        return df, encoders

    @staticmethod
    def scale_data(df, parameters):
        """数据缩放"""
        scaling_config = parameters.get('scaling', [])
        scalers = {}
        
        for config in scaling_config:
            cols = config['columns']
            method = config['method']
            
            if method == 'standard':
                scaler = StandardScaler()
                df[cols] = scaler.fit_transform(df[cols])
                scalers['standard'] = scaler
            elif method == 'minmax':
                scaler = MinMaxScaler()
                df[cols] = scaler.fit_transform(df[cols])
                scalers['minmax'] = scaler

        return df, scalers

    @staticmethod
    def split_data(df, parameters):
        """数据分割"""
        target_column = parameters['target_column']
        test_size = parameters.get('test_size', 0.2)
        val_size = parameters.get('val_size', 0.1)
        random_state = parameters.get('random_state', 42)

        # 分离特征和目标
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # 首先分割出测试集
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # 从剩余数据中分割出验证集
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=random_state
        )

        return {
            'train': (X_train, y_train),
            'val': (X_val, y_val),
            'test': (X_test, y_test)
        }

    @staticmethod
    def save_processed_data(data_dict, base_path, dataset_name):
        """保存处理后的数据"""
        saved_paths = {}
        
        for split_name, (X, y) in data_dict.items():
            # 合并特征和标签
            df = pd.concat([X, y], axis=1)
            
            # 构建保存路径
            filename = f"{dataset_name}_{split_name}.csv"
            save_path = os.path.join(base_path, filename)
            
            # 保存数据
            df.to_csv(save_path, index=False)
            saved_paths[split_name] = save_path

        return saved_paths 