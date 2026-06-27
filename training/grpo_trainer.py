try:
    from trl import GRPOTrainer, GRPOConfig
except Exception:
    GRPOTrainer = None
    GRPOConfig = None

try:
    from unsloth import FastLanguageModel
except Exception:
    FastLanguageModel = None

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


def load_model(model_name: str = MODEL_NAME):
    if FastLanguageModel is None:
        raise ImportError(
            "unsloth requires a CUDA GPU. Run training on Colab T4 or any NVIDIA/AMD/Intel GPU host."
        )
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=4096,
        load_in_4bit=True,
        fast_inference=False,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "v_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    return model, tokenizer


def get_grpo_config(output_dir: str = "./checkpoints"):
    if GRPOConfig is None:
        raise ImportError(
            "trl is required for get_grpo_config. Install with `pip install trl`."
        )
    return GRPOConfig(
        learning_rate=5e-6,
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_generations=8,
        max_new_tokens=512,
        temperature=0.9,
        output_dir=output_dir,
        logging_steps=10,
        save_steps=100,
        warmup_steps=50,
        optim="adamw_8bit",
    )
