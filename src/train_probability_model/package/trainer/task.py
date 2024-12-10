import os
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    """Parse command line arguments and set environment variables"""
    parser = argparse.ArgumentParser(description="Tennis Match Prediction Training")

    # GCS configs
    parser.add_argument("--bucket-name", type=str, required=True, help="GCS bucket name")
    parser.add_argument("--data-folder", type=str, required=True, help="Data folder path in GCS")
    parser.add_argument("--data-file", type=str, required=True, help="Data file name")

    # Model configs
    parser.add_argument("--test-size", type=float, required=True, help="Test set size ratio")
    parser.add_argument("--batch-size", type=int, required=True, help="Training batch size")
    parser.add_argument("--hidden-size", type=int, required=True, help="LSTM hidden size")
    parser.add_argument("--num-layers", type=int, required=True, help="Number of LSTM layers")
    parser.add_argument("--lr", type=float, required=True, help="Learning rate")
    parser.add_argument("--num-epochs", type=int, required=True, help="Number of training epochs")
    parser.add_argument("--wandb-key", type=str, required=True, help="Weights & Biases API key")
    parser.add_argument(
        "--run-sweep",
        type=int,
        required=True,
        help="Whether to run hyperparameter sweep (1) or not (0)",
    )
    parser.add_argument(
        "--val-f1-threshold",
        type=float,
        required=True,
        help="Validation F1 score threshold",
    )

    args = parser.parse_args()

    # Set environment variables from arguments
    os.environ["GCS_BUCKET_NAME"] = args.bucket_name
    os.environ["DATA_FOLDER"] = args.data_folder
    os.environ["DATA_FILE"] = args.data_file
    os.environ["TEST_SIZE"] = str(args.test_size)
    os.environ["BATCH_SIZE"] = str(args.batch_size)
    os.environ["HIDDEN_SIZE"] = str(args.hidden_size)
    os.environ["NUM_LAYERS"] = str(args.num_layers)
    os.environ["LR"] = str(args.lr)
    os.environ["NUM_EPOCHS"] = str(args.num_epochs)
    os.environ["WANDB_KEY"] = args.wandb_key
    os.environ["RUN_SWEEP"] = str(args.run_sweep)
    os.environ["VAL_F1_THRESHOLD"] = str(args.val_f1_threshold)

    # Log all settings
    logging.info("=== Training Configuration ===")
    logging.info(f"GCS Bucket: {args.bucket_name}")
    logging.info(f"Data Folder: {args.data_folder}")
    logging.info(f"Data File: {args.data_file}")
    logging.info(f"Test Size: {args.test_size}")
    logging.info(f"Batch Size: {args.batch_size}")
    logging.info(f"Hidden Size: {args.hidden_size}")
    logging.info(f"Number of Layers: {args.num_layers}")
    logging.info(f"Learning Rate: {args.lr}")
    logging.info(f"Number of Epochs: {args.num_epochs}")
    logging.info(f"Run Sweep: {args.run_sweep}")
    logging.info(f"Validation F1 Threshold: {args.val_f1_threshold}")
    logging.info("===========================")

    return args


def main():
    """Main entry point for the training task"""
    parse_args()

    from trainer.train_model import main as train_main

    train_main()


if __name__ == "__main__":
    main()
