from processor_regex import classify_with_regex
from processor_bert import classify_with_bert
from processor_llm import classify_with_llm
import pandas as pd

def classify(logs):
    labels=[]
    for source,log_msg in logs:
        label=classify_log(source,log_msg)
        labels.append(label)                    #(source,log_msg,label)
    return labels

def classify_log(source,log_message):
    if source=="LegacyCRM":
        label=classify_with_llm(log_message)
    else:
        label=classify_with_regex(log_message)
        if label is None:
            label=classify_with_bert(log_message)
    return label

def classify_csv(file_path):
    df=pd.read_csv(file_path)
    pairs = list(zip(df['source'], df['log_message']))
    labels=classify(pairs)
    df["target_label"]=labels
    output_file="resources/output.csv"
    df.to_csv(output_file,index=False)


#if __name__=="__main__":
    #classify_csv("resources/test.csv")
    #log_entries = [
    #    ("ModernCRM", "User User123 logged in"),
    #    ("LegacyCRM", "Lead conversion failed for prospect ID 7842 due to missing contact information."),
    #    ("ModernHR", "Account with ID 789 created by admin"),
    #    ("BillingSystem", "Backup started at 12:01 AM"),
    #    ("BillingSystem", "Backup ended at 23:59"),
    #    ("BillingSystem", "Backup completed successfully."),
    #    ("ModernCRM", "System updated to version 3.5.2"),
    #    ("ThirdPartyAPI", "File data.zip uploaded successfully by user alice"),
    #    ("AnalyticsEngine", "Disk cleanup completed successfully."),
    #    ("LegacyCRM", "The 'ExportToCSV' feature is outdated. Please migrate to 'ExportToXLSX' by the end of Q3."),
    #    ("BillingSystem", "backup Completed Successfully."),
    #    ("ModernCRM", "user user007 LOGGED In"),
    #    ("ThirdPartyAPI", "Unauthorized access detected"),
    #    ("AnalyticsEngine", "System booting up"),
    #    ("BillingSystem", "Backup failed at midnight")
    #]
    #classified_logs=classify(log_entries)
    #print(classified_logs)
    