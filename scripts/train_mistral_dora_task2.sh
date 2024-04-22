CUDA_VISIBLE_DEVICES=1 python src/train_bash.py \
--stage sft \
--model_name_or_path /home/projects/pretrained_models/nlp/mistral-7b-instruct-v0.2 \
--do_train \
--dataset ai4scup_llmkg_task2_format1 \
--finetuning_type lora \
--lora_rank 64 \
--lora_target q_proj,k_proj,v_proj,o_proj,gate_proj \
--output_dir ./output/mistral-7b-instruct-v0.2-lora-task2 \
--overwrite_cache \
--per_device_train_batch_size 4 \
--gradient_accumulation_steps 16 \
--preprocessing_num_workers 16 \
--lr_scheduler_type cosine \
--logging_steps 10 \
--save_steps 100 \
--learning_rate 5e-5 \
--max_grad_norm 0.5 \
--num_train_epochs 15 \
--plot_loss \
--fp16 \
--template mistral \
--overwrite_output_dir \
--cutoff_len 2048 \
--dataset_dir './data' \
--save_total_limit 6 \
--use_dora \


