### task1
CUDA_VISIBLE_DEVICES=1 python src/train_bash.py \
--stage sft \
--model_name_or_path /home/projects/pretrained_models/nlp/mistral-7b-instruct-v0.2 \
--do_predict \
--dataset ai4scup_llmkg_test_v5_task1-v2 \
--finetuning_type lora \
--output_dir ./output/mistral-7b-instruct-v0.2-lora-task1 \
--per_device_eval_batch_size 1 \
--preprocessing_num_workers 16 \
--logging_steps 10 \
--plot_loss \
--template mistral \
--overwrite_output_dir \
--dataset_dir './data' \
--predict_with_generate \
--generation_max_length 256 \
--cutoff_len 2048 \
--adapter_name_or_path './output/mistral-7b-instruct-v0.2-lora-task1/checkpoint-150' \
--fp16 \


#### task2
#CUDA_VISIBLE_DEVICES=1 python src/train_bash.py \
#--stage sft \
#--model_name_or_path /home/projects/pretrained_models/nlp/mistral-7b-instruct-v0.2 \
#--do_predict \
#--dataset ai4scup_llmkg_test_v5_task2 \
#--finetuning_type lora \
#--output_dir ./output/mistral-7b-instruct-v0.2-lora-task2 \
#--per_device_eval_batch_size 1 \
#--preprocessing_num_workers 16 \
#--logging_steps 10 \
#--plot_loss \
#--template mistral \
#--overwrite_output_dir \
#--dataset_dir './data' \
#--predict_with_generate \
#--generation_max_length 256 \
#--cutoff_len 2048 \
#--adapter_name_or_path './output/mistral-7b-instruct-v0.2-lora-task2/checkpoint-400' \
#--fp16 \



