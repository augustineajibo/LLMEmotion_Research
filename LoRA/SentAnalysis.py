from datasets import load_dataset, DatasetDict, Dataset
from transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer)
from peft import PeftModel, PeftConfig,get_peft_model,LoraConfig
import evaluate
import torch
import numpy as np

model_checkpoint ="distilbert-base-uncased"
#define label maps
id2label={0:"Negative", 1: "Positive"}
label2id={"Negative":0,"Positive":1}

#generate classifcation model from model_checkpoint
model= AutoModelForSequenceClassification.from_pretrained(model_checkpoint,num_labels=2,id2label=id2label,label2id=label2id)


dataset = load_dataset("shawhin/imdb-truncated")
#print(dataset)
#create tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint,add_prefix_space=True)

#create tokenization function
def tokenize_function(examples):
    #extract the text
    text = examples["text"]

    # tokenize and truncate text
    tokenizer.truncation_side="left"
    tokenized_inputs =tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        max_length=512
    )
    return tokenized_inputs

# add pad token if none exists
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    model.resize_token_embeddings(len(tokenizer))

# tokenize training and validation datasets
tokenized_datatset = dataset.map(tokenize_function, batched=True)
#print(tokenized_datatset)

#create data collator
data_collator= DataCollatorWithPadding(tokenizer=tokenizer)

#import accuracy evaluation metric
accuracy = evaluate.load("accuracy")

#define an evaluation function to pass into trainer later
def computer_metrics(p):
    predictions,labels = p
    predictions =np.argmax(predictions,axis=1)

    return {"accuracy": accuracy.compute(predictions=predictions, references=labels)}

#define list of examples
text_list=["It was good.","Not a fan, don't recommend","Better than the first one.","This is not worth watching even once",
           "This one is a pass."]

print("Untrained model predictions:")
print("-----------------------------")
"""
for text in text_list:
    #tokenize text
    inputs = tokenizer.encode(text, return_tensors="pt")
    #compute logits
    logits = model(inputs).logits

    #convert logits to label
    predictions=torch.argmax(logits)


    print(text + "-" + id2label[predictions.tolist()])
"""
#Fine turning using LoRA
peft_config=LoraConfig(task_type="SEQ_CLS", #sequence classification
                       r=4,#intrinsic rank of trainable weight matrix
                       lora_alpha=32, # learning rate
                       lora_dropout=0.01, #probability of dropout
                       target_modules=['q_lin'] #we apply lora to query layer
                       )

# Update our model to one that is fine-tuned
model = get_peft_model(model,peft_config)
model.print_trainable_parameters()

#hyperparameters
lr = 1e-3 #size of optimization step
batch_size=4 #number of examples processed per optimization step
num_epochs=10 #number of times model runs through training data

#define trainig arguments
training_args =TrainingArguments(output_dir=model_checkpoint + "-lora-text-classification",
                                 learning_rate=lr,
                                 per_device_train_batch_size=batch_size,
                                 per_device_eval_batch_size=batch_size,
                                 num_train_epochs=num_epochs,
                                 weight_decay=0.01,
                                 evaluation_strategy="epoch",
                                 save_strategy="epoch",
                                 load_best_model_at_end=True

                                 )

#create trainer object
trainer=Trainer(
    model=model, #out peft model
    args= training_args,#hyperparameters
    train_dataset=tokenized_datatset["train"],#training dat
    eval_dataset=tokenized_datatset["validation"],#validation data
    tokenizer=tokenizer, #defind tokenizer
    data_collator=data_collator,#this will dynamically pad examples in each batch
    compute_metrics=computer_metrics,#evalutes model using compute_metric function

)
#train model
trainer.train()
"""
model.to('cpu')
print("Trained model predictions:")
print("--------------------------")

for text in text_list:
    #tokenize text
    inputs = tokenizer.encode(text, return_tensors="pt").to("cpu")
    #compute logits
    logits = model(inputs).logits

    #convert logits to label
    predictions=torch.max(logits,1).indices
    print(text + "-" + id2label[predictions.tolist()[0]])

"""