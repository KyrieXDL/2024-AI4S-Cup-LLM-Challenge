#CUDA_VISIBLE_DEVICES=0 python src/train_bash.py \
#--stage sft \
#--model_name_or_path /home/projects/pretrained_models/nlp/biomistral-7b \
#--do_predict \
#--dataset ai4scup_llmkg_test_v5 \
#--finetuning_type lora \
#--lora_rank 16 \
#--lora_target q_proj,v_proj \
#--output_dir ./output/biomistral-7b-lora-external \
#--per_device_eval_batch_size 2 \
#--preprocessing_num_workers 16 \
#--logging_steps 10 \
#--plot_loss \
#--template mistral \
#--overwrite_output_dir \
#--dataset_dir './data' \
#--predict_with_generate \
#--generation_max_length 256 \
#--cutoff_len 2048 \
#--adapter_name_or_path './output/biomistral-7b-lora-external/checkpoint-880' \
#--fp16 \



CUDA_VISIBLE_DEVICES=0 python src/train_bash.py \
--stage sft \
--model_name_or_path /home/projects/pretrained_models/nlp/biomistral-7b \
--do_predict \
--dataset ai4scup_llmkg_test_v5_task1_entity \
--finetuning_type lora \
--lora_rank 16 \
--lora_target q_proj,v_proj \
--output_dir ./output/biomistral-7b-lora \
--per_device_eval_batch_size 2 \
--preprocessing_num_workers 16 \
--logging_steps 10 \
--plot_loss \
--template mistral \
--overwrite_output_dir \
--dataset_dir './data' \
--predict_with_generate \
--generation_max_length 256 \
--cutoff_len 2048 \
--adapter_name_or_path './output/biomistral-7b-lora/checkpoint-60' \
--fp16 \


#--num_beams 4 \
#--repetition_penalty 0.7 \
#--top_k 30 \


#--max_samples 10 \

