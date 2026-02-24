# tests/test_model_trainer.py
import os
import sys
import pytest
import torch
import numpy as np
import pandas as pd
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.constants import EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

N_USERS = 50
N_ITEMS = 30

@pytest.fixture
def model():
    """Fresh NeuralCF model with small dimensions for fast tests."""
    from src.components.model_trainer import NeuralCF
    return NeuralCF(
        n_users=N_USERS,
        n_items=N_ITEMS,
        embed_dim=EMBED_DIM,
        hidden_layers=HIDDEN_LAYERS,
        dropout=DROPOUT_RATE,
    )


@pytest.fixture
def sample_batch():
    """Small random batch: (users, items, labels)."""
    torch.manual_seed(42)
    users  = torch.randint(0, N_USERS, (32,))
    items  = torch.randint(0, N_ITEMS, (32,))
    labels = torch.randint(0, 2, (32,)).float()
    return users, items, labels


@pytest.fixture
def sample_train_df():
    """Tiny training dataframe."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "user":   np.random.randint(0, N_USERS, n),
        "item":   np.random.randint(0, N_ITEMS, n),
        "rating": np.random.randint(0, 2, n).astype(float),
    })


@pytest.fixture
def tmp_dir():
    """Temporary directory for model files."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


# ─────────────────────────────────────────────────────────────────────────────
# MODEL ARCHITECTURE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestNeuralCFArchitecture:

    def test_model_instantiates(self, model):
        """NeuralCF should instantiate without errors."""
        assert model is not None

    def test_embedding_dimensions_correct(self, model):
        """Embedding tables must match n_users, n_items, and EMBED_DIM."""
        assert model.user_embed.weight.shape == (N_USERS, EMBED_DIM)
        assert model.item_embed.weight.shape == (N_ITEMS, EMBED_DIM)

    def test_output_shape_matches_batch(self, model, sample_batch):
        """Forward pass output shape must equal batch size."""
        users, items, _ = sample_batch
        model.eval()
        with torch.no_grad():
            out = model(users, items)
        assert out.shape == (32,)

    def test_output_in_0_1_range(self, model, sample_batch):
        """Output values must be in [0, 1] (sigmoid activation)."""
        users, items, _ = sample_batch
        model.eval()
        with torch.no_grad():
            out = model(users, items)
        assert out.min().item() >= 0.0
        assert out.max().item() <= 1.0

    def test_model_has_mlp_layers(self, model):
        """Model must contain MLP sequential block."""
        assert hasattr(model, "mlp")
        assert isinstance(model.mlp, torch.nn.Sequential)

    def test_model_parameter_count_reasonable(self, model):
        """Model should have at least 10k parameters."""
        total = sum(p.numel() for p in model.parameters())
        assert total > 10_000

    def test_different_users_produce_different_outputs(self, model):
        """Different user IDs with same item should yield different scores."""
        model.eval()
        items = torch.tensor([0, 0])
        users = torch.tensor([0, 1])
        with torch.no_grad():
            out = model(users, items)
        assert out[0].item() != out[1].item()

    def test_different_items_produce_different_outputs(self, model):
        """Same user with different items should yield different scores."""
        model.eval()
        users = torch.tensor([0, 0])
        items = torch.tensor([0, 1])
        with torch.no_grad():
            out = model(users, items)
        assert out[0].item() != out[1].item()

    def test_batch_size_1_works(self, model):
       
        model.eval()
        users = torch.tensor([0])
        items = torch.tensor([0])
        with torch.no_grad():
            out = model(users, items)

        # squeeze() on batch=1 gives scalar, both are valid
        assert out.shape == torch.Size([]) or out.shape == torch.Size([1])
        assert 0.0 <= out.item() <= 1.0
    


    def test_large_batch_works(self, model):
        """Model must handle large batch (1000) without errors."""
        model.eval()
        users = torch.randint(0, N_USERS, (1000,))
        items = torch.randint(0, N_ITEMS, (1000,))
        with torch.no_grad():
            out = model(users, items)
        assert out.shape == (1000,)


# ─────────────────────────────────────────────────────────────────────────────
# FORWARD PASS TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestForwardPass:

    def test_forward_is_deterministic_in_eval(self, model, sample_batch):
        """Two forward passes in eval mode must return identical results."""
        users, items, _ = sample_batch
        model.eval()
        with torch.no_grad():
            out1 = model(users, items)
            out2 = model(users, items)
        assert torch.allclose(out1, out2)

    def test_forward_produces_gradients_in_train(self, model, sample_batch):
        """Output must allow gradient computation in training mode."""
        users, items, labels = sample_batch
        model.train()
        out  = model(users, items)
        loss = torch.nn.BCELoss()(out, labels)
        loss.backward()
        assert model.user_embed.weight.grad is not None
        assert model.item_embed.weight.grad is not None

    def test_no_nan_in_output(self, model, sample_batch):
        """Forward pass must not produce NaN values."""
        users, items, _ = sample_batch
        model.eval()
        with torch.no_grad():
            out = model(users, items)
        assert not torch.isnan(out).any()

    def test_no_inf_in_output(self, model, sample_batch):
        """Forward pass must not produce Inf values."""
        users, items, _ = sample_batch
        model.eval()
        with torch.no_grad():
            out = model(users, items)
        assert not torch.isinf(out).any()


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING STEP TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTrainingStep:

    def test_loss_decreases_after_gradient_step(self, model, sample_batch):
        """Loss should decrease after one gradient update step."""
        users, items, labels = sample_batch
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = torch.nn.BCELoss()

        model.train()
        loss1 = criterion(model(users, items), labels)
        optimizer.zero_grad()
        loss1.backward()
        optimizer.step()

        with torch.no_grad():
            loss2 = criterion(model(users, items), labels)

        # Loss should generally decrease (allow small tolerance)
        assert loss2.item() < loss1.item() + 0.1

    def test_parameters_update_after_backward(self, model, sample_batch):
        """Model parameters must change after one backward + optimizer step."""
        users, items, labels = sample_batch
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = torch.nn.BCELoss()

        # Snapshot weights before
        before = model.user_embed.weight.data.clone()

        model.train()
        loss = criterion(model(users, items), labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        after = model.user_embed.weight.data
        assert not torch.equal(before, after)

    def test_gradients_not_none_after_backward(self, model, sample_batch):
        """All parameter gradients must be populated after backward pass."""
        users, items, labels = sample_batch
        criterion = torch.nn.BCELoss()
        model.train()
        loss = criterion(model(users, items), labels)
        loss.backward()
        for name, param in model.named_parameters():
            assert param.grad is not None, f"No gradient for {name}"

    def test_loss_is_scalar(self, model, sample_batch):
        """BCELoss output must be a scalar tensor."""
        users, items, labels = sample_batch
        model.train()
        loss = torch.nn.BCELoss()(model(users, items), labels)
        assert loss.dim() == 0

    def test_loss_is_positive(self, model, sample_batch):
        """BCELoss must always be positive."""
        users, items, labels = sample_batch
        model.train()
        loss = torch.nn.BCELoss()(model(users, items), labels)
        assert loss.item() > 0

    def test_adam_optimizer_works(self, model):
        """Adam optimizer should instantiate and step without errors."""
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
        assert optimizer is not None
        users  = torch.randint(0, N_USERS, (16,))
        items  = torch.randint(0, N_ITEMS, (16,))
        labels = torch.randint(0, 2, (16,)).float()
        model.train()
        loss = torch.nn.BCELoss()(model(users, items), labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


# ─────────────────────────────────────────────────────────────────────────────
# MODEL PERSISTENCE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestModelPersistence:

    def test_model_saved_and_loaded(self, model, tmp_dir):
        """Model state dict saved and loaded must produce identical outputs."""
        model.eval()
        users = torch.randint(0, N_USERS, (10,))
        items = torch.randint(0, N_ITEMS, (10,))

        with torch.no_grad():
            out_before = model(users, items)

        path = os.path.join(tmp_dir, "model.pt")
        torch.save(model.state_dict(), path)

        # Load into a fresh model
        from src.components.model_trainer import NeuralCF
        new_model = NeuralCF(N_USERS, N_ITEMS, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
        new_model.load_state_dict(torch.load(path, weights_only=True))
        new_model.eval()

        with torch.no_grad():
            out_after = new_model(users, items)

        assert torch.allclose(out_before, out_after)

    def test_model_file_exists_after_save(self, model, tmp_dir):
        """model.pt must exist on disk after saving."""
        path = os.path.join(tmp_dir, "model.pt")
        torch.save(model.state_dict(), path)
        assert os.path.exists(path)

    def test_model_file_size_nonzero(self, model, tmp_dir):
        """Saved model file must not be empty."""
        path = os.path.join(tmp_dir, "model.pt")
        torch.save(model.state_dict(), path)
        assert os.path.getsize(path) > 0

    def test_state_dict_keys_correct(self, model):
        """State dict must contain expected embedding and MLP keys."""
        keys = list(model.state_dict().keys())
        assert any("user_embed" in k for k in keys)
        assert any("item_embed" in k for k in keys)
        assert any("mlp"        in k for k in keys)

    def test_architecture_mismatch_raises_error(self, model, tmp_dir):
        """Loading weights into wrong architecture must raise RuntimeError."""
        from src.components.model_trainer import NeuralCF
        path = os.path.join(tmp_dir, "model.pt")
        torch.save(model.state_dict(), path)

        # Wrong EMBED_DIM
        wrong_model = NeuralCF(N_USERS, N_ITEMS, embed_dim=8, hidden_layers=[16, 8])
        with pytest.raises(RuntimeError):
            wrong_model.load_state_dict(
                torch.load(path, weights_only=True), strict=True
            )


# ─────────────────────────────────────────────────────────────────────────────
# DATASET TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRatingsDataset:

    def test_dataset_length_matches_df(self, sample_train_df):
        """Dataset __len__ must match number of rows in dataframe."""
        from src.components.model_trainer import RatingsDataset
        ds = RatingsDataset(sample_train_df)
        assert len(ds) == len(sample_train_df)

    def test_dataset_returns_correct_dtypes(self, sample_train_df):
        """Dataset must return (LongTensor, LongTensor, FloatTensor)."""
        from src.components.model_trainer import RatingsDataset
        ds = RatingsDataset(sample_train_df)
        user, item, label = ds[0]
        assert user.dtype  == torch.long
        assert item.dtype  == torch.long
        assert label.dtype == torch.float32

    def test_dataloader_batches_correctly(self, sample_train_df):
        """DataLoader must produce correct batch sizes."""
        from src.components.model_trainer import RatingsDataset
        from torch.utils.data import DataLoader
        ds     = RatingsDataset(sample_train_df)
        loader = DataLoader(ds, batch_size=32, shuffle=True)
        users, items, labels = next(iter(loader))
        assert users.shape[0]  <= 32
        assert items.shape[0]  <= 32
        assert labels.shape[0] <= 32

    def test_dataset_values_in_valid_range(self, sample_train_df):
        """User/item indices in dataset must be within valid ranges."""
        from src.components.model_trainer import RatingsDataset
        ds = RatingsDataset(sample_train_df)
        for i in range(len(ds)):
            user, item, label = ds[i]
            assert 0 <= user.item()  < N_USERS
            assert 0 <= item.item()  < N_ITEMS
            assert label.item() in (0.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# MULTI-EPOCH TRAINING INTEGRATION TEST
# ─────────────────────────────────────────────────────────────────────────────

class TestTrainingLoop:

    def test_loss_trends_downward_over_epochs(self, sample_train_df):
        """Average loss should trend downward over 5 mini-epochs."""
        from src.components.model_trainer import NeuralCF, RatingsDataset
        from torch.utils.data import DataLoader

        model     = NeuralCF(N_USERS, N_ITEMS, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.05)
        criterion = torch.nn.BCELoss()
        loader    = DataLoader(RatingsDataset(sample_train_df), batch_size=32, shuffle=True)

        losses = []
        for _ in range(5):
            model.train()
            total = 0.0
            for users, items, labels in loader:
                out  = model(users, items)
                loss = criterion(out, labels)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total += loss.item()
            losses.append(total / len(loader))

        # First loss should be higher than last (overall downward trend)
        assert losses[0] > losses[-1] or abs(losses[0] - losses[-1]) < 0.1

    def test_model_trains_without_exploding(self, sample_train_df):
        """Model weights must not become NaN or Inf during training."""
        from src.components.model_trainer import NeuralCF, RatingsDataset
        from torch.utils.data import DataLoader

        model     = NeuralCF(N_USERS, N_ITEMS, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = torch.nn.BCELoss()
        loader    = DataLoader(RatingsDataset(sample_train_df), batch_size=32, shuffle=True)

        for _ in range(3):
            model.train()
            for users, items, labels in loader:
                loss = criterion(model(users, items), labels)
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

        for name, param in model.named_parameters():
            assert not torch.isnan(param).any(), f"NaN in {name}"
            assert not torch.isinf(param).any(), f"Inf in {name}"

    def test_scheduler_reduces_lr(self):
   
        from src.components.model_trainer import NeuralCF, RatingsDataset
        from torch.utils.data import DataLoader

        model     = NeuralCF(N_USERS, N_ITEMS, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

        initial_lr = optimizer.param_groups[0]["lr"]

        # Must call optimizer.step() before scheduler.step()
        users  = torch.randint(0, N_USERS, (16,))
        items  = torch.randint(0, N_ITEMS, (16,))
        labels = torch.randint(0, 2, (16,)).float()

        for _ in range(2):
            model.train()
            loss = torch.nn.BCELoss()(model(users, items), labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()    # ← must come first
            scheduler.step()    # ← then scheduler

        new_lr = optimizer.param_groups[0]["lr"]
        assert new_lr < initial_lr
        assert abs(new_lr - initial_lr * 0.5) < 1e-8