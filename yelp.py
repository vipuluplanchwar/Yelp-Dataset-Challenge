import csv
import json
import ast


def removing_null_rows(path_to_csv='reviews.csv'):
    """
    The csv contained altering rows filled with the business id and 
    categories json dump
    We need to remove the blank rows and create a new csv in the process
    """
    all_dict =[]
    with open(path_to_csv,'rb') as infile:
        # reading the file as a dict. the key would be the column names 
        # and the values would be the cell contents across the columns
        reader = csv.DictReader(infile)
        for r in reader:
            # if the row is blank, pass the iteration
            if r.get('business_id') == '':
                pass
            else:
                # r['business_id'] = r['business_id'].replace('b\'','\'')
                all_dict.append(r)

    with open('business.csv','wb') as outfile:
        fieldnames = ['business_id', 'categories']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # iterate through the dict and write in the csv
        for row in all_dict:
            writer.writerow(row)

def creating_dict_all_businesses(path_to_business_csv='business.csv'):
    """
    Returns an array of all the businesses present in the dataset
    create an array of dictionaries
    all_businesses = [
            {
            'business_id': "b'qwertyu'",
            'categories': ['A', 'B', 'C']
            },
            {
            'business_id': "b'asdfghj'",
            'categories': ['X', 'Z', 'Y']
            }
    ]
    """
    with open('business.csv', 'rb') as infile:
        reader = csv.DictReader(infile)
        all_business = []
        for r in reader:
            curr_business = {}
            print r['business_id']
            # curr_business['business_id'] = ast.literal_eval(r['business_id'])
            # print curr_business['business_id']
            curr_business['business_id'] = r['business_id']
            # converting the json to python literal
            curr_business['categories'] = ast.literal_eval(r['categories'])
            all_business.append(curr_business)

    print len(all_business)
    return all_business

def specific_cuisine(raw_cuisine):
    """
    Used to map out specific cuisines such as American (Old), American (Traditional), American (Fast Food)
    to a list for checking the availability
    """
    all_cuisines = []
    for cuisine in raw_cuisine:
        
        if cuisine.split(' '):
            all_cuisines.extend(cuisine.split(' '))
        else:
            all_cuisines.extend(cuisine)
    return all_cuisines

def getting_business_id(all_business, cuisine = 'Indian'):
    
    required_business = [curr_business.get('business_id') for curr_business in all_business if cuisine in specific_cuisine(curr_business.get('categories'))]

    require_dict = [curr_business for curr_business in all_business if cuisine in specific_cuisine(curr_business.get('categories'))]

    with open('required_business.csv','wb') as outfile:
        fieldnames = ['business_id', 'categories']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in require_dict:
            writer.writerow(row)

    return required_business, require_dict

def writing_reviews(required_businesses, cuisine, path_to_csv='yelp_academic_dataset_review.csv', polarity=1, max_business = 1000):

    with open(path_to_csv,'rb') as infile:
        # reading the entire dataset as a dir()
        reader = csv.DictReader(infile)
        all_reviews = {}
        tot_business = 0
        for r in reader:
            # max unq businesses
            if (tot_business <= max_business):
                business_id = r.get('business_id')
                if business_id in required_businesses:
                    
                    # cleaning the reviews
                    raw_reviews = r.get('text')
                    clean_reviews = ast.literal_eval(raw_reviews)
                    
                    # creating an array of the reviews for unq business
                    if all_reviews.get(business_id, None):
                        curr_value = all_reviews.get(business_id)
                        print 'appending review ', len(curr_value), 'for business_id', business_id
                        curr_value.append(clean_reviews)
                        all_reviews[business_id] = curr_value
                    else:
                        print 'creating review for business_id ' + business_id
                        all_reviews[business_id] = [clean_reviews]
                        tot_business += 1

    if polarity:
        review_filename = "yelp_reviews_1_" + cuisine + ".csv"
    else:
        review_filename = "yelp_reviews_0_" + cuisine + ".csv"

    with open(review_filename, 'wb') as outfile:
        print "writing the review csv in ", review_filename
        print len(all_reviews)
        writer = csv.writer(outfile)
        writer.writerow(['Business_id','Review','Polarity'])

        for business_id, business_reviews in all_reviews.iteritems():
            print 'creating the dict'            
            reviews = [curr_review.replace('\n',' ') for curr_review in business_reviews]
            print business_id, len(reviews)
            reviews = ' '.join(reviews)

            print reviews
            writer.writerow([business_id, reviews, polarity])
    
    return all_reviews
       
def getting_business_id_inverse(all_business, cuisine = 'Nightlife', max_count=999):
    other_business = []
    print 'getting other business with max of', max_count 
    
    # find the first n business ids for which categories does not contain the cuisine
    other_business = [curr_business.get('business_id') for curr_business in all_business if (cuisine not in specific_cuisine(curr_business.get('categories')) and (len(other_business) < max_count))]

    require_dict = [curr_business for curr_business in all_business if (cuisine not in specific_cuisine(curr_business.get('categories')) and (len(other_business) < max_count))]

    with open('other_business.csv','wb') as outfile:
        fieldnames = ['business_id', 'categories']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in require_dict:
            writer.writerow(row)

    return other_business, require_dict

if __name__ == '__main__':
    
    # removing the null rows
    removing_null_rows()

    # create an array of all the businesses
    all_business = creating_dict_all_businesses()
    
    # finding the cuisine specific business
    required_cuisine = None
    while not required_cuisine:
        required_cuisine = raw_input("Enter a cuisine \n>>  ")

    required_business, required_dict = getting_business_id(all_business, required_cuisine)
    all_reviews = writing_reviews(required_business, required_cuisine, polarity=1)
    max_count = len(all_reviews)
    print max_count
    
    # finding the businesses other than required cuisine and match the total enteries 
    # to maintain the polarity levels
    other_business, other_req_dict = getting_business_id_inverse(all_business, 'Indian', max_count=max_count)

    # creating the polarity 0 csv
    other_reviews = writing_reviews(other_business, required_cuisine, polarity=0)

    print '~' * 10

    print max_count
