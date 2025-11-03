from collections import Counter
from os import environ
import matplotlib.pyplot as plt
import pymongo
from pymongo.synchronous.collection import Collection

from helpers.word_class_embeddings import visualize_word_class_clusters

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    
    plt.rcParams.update({'font.size': 16})

    viz_type = input("Please select which data to visualize:\n  1. Dates\n  2. Text class frequencies\n  3. Text class embedding clustering (computation heavy)\n [1-3]: ")
    match viz_type:
        case "1":
            visualize_dates(collection)
        case "2":
            visualize_text_class_frequency(collection)
        case "3":
            visualize_text_class_clustering(collection)
        case _:
            print("Please input a number in the indicated range. Exiting...")



def visualize_dates(collection: Collection):
    print("Getting min/max dates from the database...")
    dates = list(collection.find({}, {"date_range": 1, "_id": 0}))
    date_ranges = [date.get("date_range", {}) for date in dates]
    min_dates = [int(min_date["y"]) for date_range in date_ranges if (min_date := date_range.get("min")) is not None]
    max_dates = [int(max_date["y"]) for date_range in date_ranges if (max_date := date_range.get("max")) is not None]
    mean_dates = [int((max_date + min_date) / 2) for (min_date, max_date) in zip(min_dates, max_dates)]

    fig, axs = plt.subplots(1, 3, sharex=True, sharey=True)
    # Plot minimum dates
    axs[0].hist(min_dates, bins=30)
    axs[0].set_title("Minimum dates")
    axs[0].set_xlabel("Year")
    axs[0].set_ylabel("# occurrences in database")
    # Max dates 
    axs[1].hist(max_dates, bins=30)
    axs[1].set_title("Maximum dates")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("# occurrences in database")
    # Mean dates 
    axs[2].hist(mean_dates, bins=30, color='orange')
    axs[2].set_title("Mean dates")
    axs[2].set_xlabel("Year")
    axs[2].set_ylabel("# occurrences in database")
    plt.show()

def visualize_text_class_frequency(collection: Collection):
    while True:
        max_n_input = input("Show top N text classes\n [1-..]: ")
        try:
            if (max_n := int(max_n_input)) >= 1:
                break
            else:
                print("Please enter a number greater than 1")
        except ValueError:
            print("Please enter a number")
    print("Getting min/max dates from the database...")
    all_classes_cursor = collection.find({}, {"text_classes": 1, "_id": 0})
    all_classes = [text_classes for db_record in all_classes_cursor if (text_classes := db_record.get("text_classes")) is not None]
    
    classes_flat = []
    for single_papyrus_classes in all_classes:
        classes_flat.extend(single_papyrus_classes)
    counter = Counter(classes_flat)
    labels, counts = zip(*counter.most_common(max_n))
    plt.bar(labels, counts)
    plt.show()

def visualize_text_class_clustering(collection: Collection):
    all_classes_cursor = collection.find({}, {"text_classes": 1, "_id": 0})
    all_classes = [text_classes for db_record in all_classes_cursor if (text_classes := db_record.get("text_classes")) is not None]
    all_classes_flat = []
    for classes_single_papyrus in all_classes:
#        all_classes_flat.extend(classes_single_papyrus)
        if len(classes_single_papyrus) > 0:
            all_classes_flat.append(classes_single_papyrus[0])

    visualize_word_class_clusters(all_classes_flat, num_clusters=10, visualize_limit=50000, num_labels=35)

if __name__=="__main__":
    main()
