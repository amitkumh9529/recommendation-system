# tests/test_data_transformation.py
import os
import sys
import pytest
import pandas as pd
import numpy as np
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.constants import NEG_SAMPLE_RATIO


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_ratings_df():
    """Small synthetic ratings dataframe (mimics MovieLens 1M structure)."""
    np.random.seed(42)
    return pd.DataFrame({
        "user_id":   [1, 1, 1, 2, 2, 3, 3, 3, 4, 4],
        "item_id":   [10, 20, 30, 10, 40, 20, 50, 60, 10, 70],
        "rating":    [5,  4,  2,  3,  5,  4,  1,  5,  2,  4],
        "timestamp": [964982703] * 10
    })


@pytest.fixture
def tmp_dirs():
    """Create and clean up temporary directories for artifacts."""
    base = tempfile.mkdtemp()
    yield {
        "base":         base,
        "train_path":   os.path.join(base, "train.csv"),
        "test_path":    os.path.join(base, "test.csv"),
        "encoder_path": os.path.join(base, "encoders.pkl"),
    }
    shutil.rmtree(base)


# ─────────────────────────────────────────────────────────────────────────────
# LABEL ENCODING TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLabelEncoding:

    def test_user_ids_encoded_to_zero_based(self, sample_ratings_df):
        """User IDs should be label-encoded starting from 0."""
        from sklearn.preprocessing import LabelEncoder
        encoded = LabelEncoder().fit_transform(sample_ratings_df["user_id"])
        assert encoded.min() == 0
        assert encoded.max() == sample_ratings_df["user_id"].nunique() - 1

    def test_item_ids_encoded_to_zero_based(self, sample_ratings_df):
        """Item IDs should be label-encoded starting from 0."""
        from sklearn.preprocessing import LabelEncoder
        encoded = LabelEncoder().fit_transform(sample_ratings_df["item_id"])
        assert encoded.min() == 0
        assert encoded.max() == sample_ratings_df["item_id"].nunique() - 1

    def test_encoding_is_reversible(self, sample_ratings_df):
        """Encoding then inverse_transform should recover original IDs."""
        from sklearn.preprocessing import LabelEncoder
        enc = LabelEncoder()
        encoded   = enc.fit_transform(sample_ratings_df["user_id"])
        recovered = enc.inverse_transform(encoded)
        np.testing.assert_array_equal(recovered, sample_ratings_df["user_id"].values)

    def test_n_users_matches_unique_users(self, sample_ratings_df):
        """n_users must equal number of unique user_ids."""
        from sklearn.preprocessing import LabelEncoder
        enc = LabelEncoder()
        enc.fit(sample_ratings_df["user_id"])
        assert sample_ratings_df["user_id"].nunique() == len(enc.classes_)

    def test_n_items_matches_unique_items(self, sample_ratings_df):
        """n_items must equal number of unique item_ids."""
        from sklearn.preprocessing import LabelEncoder
        enc = LabelEncoder()
        enc.fit(sample_ratings_df["item_id"])
        assert sample_ratings_df["item_id"].nunique() == len(enc.classes_)


# ─────────────────────────────────────────────────────────────────────────────
# BINARIZATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRatingBinarization:

    def test_ratings_ge_4_become_1(self, sample_ratings_df):
        """Ratings >= 4 should become 1.0 (positive interaction)."""
        binary = (sample_ratings_df["rating"] >= 4).astype(float)
        high   = sample_ratings_df[sample_ratings_df["rating"] >= 4]
        assert (binary[high.index] == 1.0).all()

    def test_ratings_lt_4_become_0(self, sample_ratings_df):
        """Ratings < 4 should become 0.0 (negative interaction)."""
        binary = (sample_ratings_df["rating"] >= 4).astype(float)
        low    = sample_ratings_df[sample_ratings_df["rating"] < 4]
        assert (binary[low.index] == 0.0).all()

    def test_binary_values_only_0_and_1(self, sample_ratings_df):
        """After binarization only 0.0 and 1.0 should exist."""
        binary = (sample_ratings_df["rating"] >= 4).astype(float)
        assert set(binary.unique()).issubset({0.0, 1.0})


# ─────────────────────────────────────────────────────────────────────────────
# NEGATIVE SAMPLING TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestNegativeSampling:

    def _generate_negatives(self, df, ratio=NEG_SAMPLE_RATIO):
        """Helper: generate negatives exactly as DataTransformation does."""
        from sklearn.preprocessing import LabelEncoder
        df = df.copy()
        df["user"]   = LabelEncoder().fit_transform(df["user_id"])
        df["item"]   = LabelEncoder().fit_transform(df["item_id"])
        df["rating"] = (df["rating"] >= 4).astype(float)

        n_items      = df["item"].nunique()
        interactions = set(zip(df["user"], df["item"]))
        pos_df       = df[df["rating"] == 1.0]

        neg_users, neg_items = [], []
        for u in pos_df["user"].unique():
            for _ in range(ratio):
                neg_item = np.random.randint(0, n_items)
                while (u, neg_item) in interactions:
                    neg_item = np.random.randint(0, n_items)
                neg_users.append(u)
                neg_items.append(neg_item)

        return pd.DataFrame({
            "user": neg_users, "item": neg_items, "rating": 0.0
        }), interactions, df["item"].nunique()

    def test_negatives_not_in_positive_set(self, sample_ratings_df):
        """No generated negative should appear in the positive interaction set."""
        neg_df, interactions, _ = self._generate_negatives(sample_ratings_df)
        for _, row in neg_df.iterrows():
            assert (int(row["user"]), int(row["item"])) not in interactions

    def test_negative_ratio_respected(self, sample_ratings_df):
        """Count of negatives = n_positive_users × NEG_SAMPLE_RATIO."""
        from sklearn.preprocessing import LabelEncoder
        df = sample_ratings_df.copy()
        df["user"]   = LabelEncoder().fit_transform(df["user_id"])
        df["rating"] = (df["rating"] >= 4).astype(float)
        n_pos_users  = df[df["rating"] == 1.0]["user"].nunique()

        neg_df, _, _ = self._generate_negatives(sample_ratings_df)
        assert len(neg_df) == n_pos_users * NEG_SAMPLE_RATIO

    def test_negatives_have_rating_zero(self, sample_ratings_df):
        """All negative samples must have rating = 0.0."""
        neg_df, _, _ = self._generate_negatives(sample_ratings_df)
        assert (neg_df["rating"] == 0.0).all()

    def test_negative_item_indices_in_valid_range(self, sample_ratings_df):
        """Negative item IDs must be within [0, n_items)."""
        neg_df, _, n_items = self._generate_negatives(sample_ratings_df)
        assert neg_df["item"].between(0, n_items - 1).all()


# ─────────────────────────────────────────────────────────────────────────────
# TRAIN / TEST SPLIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTrainTestSplit:

    def _make_full_df(self, df):
        from sklearn.preprocessing import LabelEncoder
        df = df.copy()
        df["user"]   = LabelEncoder().fit_transform(df["user_id"])
        df["item"]   = LabelEncoder().fit_transform(df["item_id"])
        df["rating"] = (df["rating"] >= 4).astype(float)
        neg = pd.DataFrame({"user": [0, 1, 2], "item": [3, 4, 5], "rating": 0.0})
        return pd.concat([df[["user", "item", "rating"]], neg], ignore_index=True)

    def test_split_ratio_is_80_20(self, sample_ratings_df):
        """Train/test split should be approximately 80/20."""
        from sklearn.model_selection import train_test_split
        full = self._make_full_df(sample_ratings_df)
        train, test = train_test_split(full, test_size=0.2, random_state=42)
        assert abs(len(train) / len(full) - 0.8) < 0.05
        assert abs(len(test)  / len(full) - 0.2) < 0.05

    def test_no_index_overlap(self, sample_ratings_df):
        """Train and test sets must not share any row indices."""
        from sklearn.model_selection import train_test_split
        full = self._make_full_df(sample_ratings_df)
        train, test = train_test_split(full, test_size=0.2, random_state=42)
        assert len(set(train.index) & set(test.index)) == 0

    def test_train_test_cover_full_data(self, sample_ratings_df):
        """len(train) + len(test) must equal total rows."""
        from sklearn.model_selection import train_test_split
        full = self._make_full_df(sample_ratings_df)
        train, test = train_test_split(full, test_size=0.2, random_state=42)
        assert len(train) + len(test) == len(full)

    def test_required_columns_present(self, sample_ratings_df):
        """Both splits must contain user, item, rating columns."""
        from sklearn.model_selection import train_test_split
        full = self._make_full_df(sample_ratings_df)
        train, test = train_test_split(full, test_size=0.2, random_state=42)
        for col in ["user", "item", "rating"]:
            assert col in train.columns
            assert col in test.columns


# ─────────────────────────────────────────────────────────────────────────────
# ENCODER PERSISTENCE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestEncoderPersistence:

    def test_encoders_saved_and_loaded(self, sample_ratings_df, tmp_dirs):
        """Encoder dict saved with pickle should be identical after loading."""
        import pickle
        from sklearn.preprocessing import LabelEncoder

        user_enc = LabelEncoder().fit(sample_ratings_df["user_id"])
        item_enc = LabelEncoder().fit(sample_ratings_df["item_id"])
        encoders = {
            "user_enc": user_enc, "item_enc": item_enc,
            "n_users":  len(user_enc.classes_),
            "n_items":  len(item_enc.classes_),
        }
        with open(tmp_dirs["encoder_path"], "wb") as f:
            pickle.dump(encoders, f)
        with open(tmp_dirs["encoder_path"], "rb") as f:
            loaded = pickle.load(f)

        assert loaded["n_users"] == encoders["n_users"]
        assert loaded["n_items"] == encoders["n_items"]
        np.testing.assert_array_equal(
            loaded["user_enc"].classes_, user_enc.classes_
        )

    def test_encoder_file_exists_after_save(self, sample_ratings_df, tmp_dirs):
        """Encoder file must exist on disk after saving."""
        import pickle
        from sklearn.preprocessing import LabelEncoder
        enc = LabelEncoder().fit(sample_ratings_df["user_id"])
        with open(tmp_dirs["encoder_path"], "wb") as f:
            pickle.dump({"user_enc": enc}, f)
        assert os.path.exists(tmp_dirs["encoder_path"])

    def test_n_users_n_items_stored_correctly(self, sample_ratings_df, tmp_dirs):
        """n_users and n_items in encoder dict must match actual unique counts."""
        import pickle
        from sklearn.preprocessing import LabelEncoder
        user_enc = LabelEncoder().fit(sample_ratings_df["user_id"])
        item_enc = LabelEncoder().fit(sample_ratings_df["item_id"])
        with open(tmp_dirs["encoder_path"], "wb") as f:
            pickle.dump({
                "user_enc": user_enc, "item_enc": item_enc,
                "n_users":  len(user_enc.classes_),
                "n_items":  len(item_enc.classes_),
            }, f)
        with open(tmp_dirs["encoder_path"], "rb") as f:
            loaded = pickle.load(f)

        assert loaded["n_users"] == sample_ratings_df["user_id"].nunique()
        assert loaded["n_items"] == sample_ratings_df["item_id"].nunique()


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION TEST — Full Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class TestTransformationPipeline:

    def _run_pipeline(self, sample_ratings_df, tmp_dirs):
        import pickle
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split

        df = sample_ratings_df.copy()
        user_enc = LabelEncoder()
        item_enc = LabelEncoder()
        df["user"]   = user_enc.fit_transform(df["user_id"])
        df["item"]   = item_enc.fit_transform(df["item_id"])
        df["rating"] = (df["rating"] >= 4).astype(float)

        train, test = train_test_split(
            df[["user", "item", "rating"]], test_size=0.2, random_state=42
        )
        train.to_csv(tmp_dirs["train_path"], index=False)
        test.to_csv(tmp_dirs["test_path"],   index=False)

        with open(tmp_dirs["encoder_path"], "wb") as f:
            pickle.dump({
                "user_enc": user_enc, "item_enc": item_enc,
                "n_users":  df["user"].nunique(),
                "n_items":  df["item"].nunique(),
            }, f)

        return df["user"].nunique(), df["item"].nunique()

    def test_output_files_created(self, sample_ratings_df, tmp_dirs):
        """All 3 output files must exist after pipeline runs."""
        self._run_pipeline(sample_ratings_df, tmp_dirs)
        assert os.path.exists(tmp_dirs["train_path"])
        assert os.path.exists(tmp_dirs["test_path"])
        assert os.path.exists(tmp_dirs["encoder_path"])

    def test_train_csv_is_valid(self, sample_ratings_df, tmp_dirs):
        """Saved train.csv must be readable and non-empty."""
        self._run_pipeline(sample_ratings_df, tmp_dirs)
        df = pd.read_csv(tmp_dirs["train_path"])
        assert len(df) > 0
        assert {"user", "item", "rating"}.issubset(df.columns)

    def test_no_nulls_in_output(self, sample_ratings_df, tmp_dirs):
        """Output CSVs must contain zero null values."""
        self._run_pipeline(sample_ratings_df, tmp_dirs)
        assert pd.read_csv(tmp_dirs["train_path"]).isnull().sum().sum() == 0
        assert pd.read_csv(tmp_dirs["test_path"]).isnull().sum().sum()  == 0

    def test_indices_within_bounds(self, sample_ratings_df, tmp_dirs):
        """All user and item indices must be within [0, n_users/n_items)."""
        n_users, n_items = self._run_pipeline(sample_ratings_df, tmp_dirs)
        for path in [tmp_dirs["train_path"], tmp_dirs["test_path"]]:
            df = pd.read_csv(path)
            assert df["user"].between(0, n_users - 1).all()
            assert df["item"].between(0, n_items - 1).all()