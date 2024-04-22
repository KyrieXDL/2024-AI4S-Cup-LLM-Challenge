CUDA_VISIBLE_DEVICES=1 python src/train_bash.py \
--stage sft \
--model_name_or_path /home/projects/pretrained_models/nlp/mistral-7b-instruct-v0.2 \
--do_train \
--dataset ai4scup_llmkg_v5_task1_multitask \
--finetuning_type full \
--output_dir ./output/mistral-7b-instruct-v0.2-galore \
--overwrite_cache \
--per_device_train_batch_size 1 \
--gradient_accumulation_steps 64 \
--preprocessing_num_workers 16 \
--lr_scheduler_type cosine \
--logging_steps 10 \
--save_steps 10 \
--learning_rate 5e-5 \
--max_grad_norm 0.5 \
--num_train_epochs 15 \
--plot_loss \
--fp16 \
--template mistral \
--overwrite_output_dir \
--cutoff_len 2560 \
--dataset_dir './data' \
--save_total_limit 6 \
--use_galore \
--galore_target mlp,self_attn \




