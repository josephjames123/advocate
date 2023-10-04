import random
import csv

# Define the number of lawyers in the dataset
num_lawyers = 10000

# List of possible specializations
specializations = ["Criminal Law", "Family Law", "Corporate Law", "Immigration Law", "Personal Injury"]

# List of possible locations
locations = ["Kottayam Distict Court", "Chanagancherry Munsiff court", "Chagancherry Court", "Kanjirapally Court", "Kanjirapally Munsiff court", "High Court"]

# Initialize an empty list to store the dataset
lawyer_dataset = []

# Generate the dataset with unique lawyer IDs
for lawyer_id in range(1, num_lawyers + 1):
    rating = round(random.uniform(1, 5), 2)  # Random rating between 1 and 5
    specialization = random.choice(specializations)
    experience_date = random.randint(2015, 2023)  # Random year between 1990 and 2023
    location = random.choice(locations)
    budget = round(random.uniform(1000, 2000), 0)  # Random budget between 1 and 100
    
    lawyer_dataset.append([lawyer_id, rating, specialization, experience_date, location, budget])

# Sort the dataset by experience date in descending order (higher experience first)
lawyer_dataset.sort(key=lambda x: x[3], reverse=True)

# Write the dataset to a CSV file
with open("lawyer_dataset.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Lawyer ID", "Rating", "Specialization", "Experience Date", "Location", "Budget"])
    writer.writerows(lawyer_dataset)

print("Dataset created and saved as 'lawyer_dataset.csv'")