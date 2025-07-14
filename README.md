# AnswerKing-AWS-DynamoDB
AnswerKing is an ordering system built with AWS Lambda, API Gateway and DynamoDB. It allows for
creation, update, and deletion of categories, items, and orders via RESTful endpoints. It's 
designed to be fast and demonstrate best practices with RESTful APIs, testing and DynamoDB design.

// Tech Stack //
- AWS Lambda – serverless compute for all business logic
- API Gateway – exposing RESTful endpoints
- DynamoDB – fully managed NoSQL database
- SAM (Serverless Application Model) – infrastructure as code
- Python (3.13) – language of choice
- Pytest – for unit testing
- Postman – for manual API testing and simulation

// Deployment Notes //
Run "sam build && sam deploy" in the terminal 

# Key Points:

// Best Practice of DynamoDB //
DynamoDB is designed for denormalized, read-optimized data, meaning it doesn’t support joins
like traditional relational databases. In this project, rather than linking orders to item IDs
and performing lookups at read time, we store the full item information (item ID, quantity,
and price) directly within each order.

This:
- Reduces the need for expensive queries later
- Keeps reads fast and efficient

// DynamoDB processes number using Decimal, JSON uses int/float they are not compatible //
DynamoDB works with numbers using a Decimal format. Therefore, as a safety feature 
I have converted numbers to string first, followed by Decimal to make sure the 
format is correct and safe to use without causing errors. I also have a custom
DecimalEncoder which I use to help me with this.

// GSI - Global Secondary Index // 
GSIs in DynamoDB let you query data using non-primary key attributes. So we can query on
different fields instead of just the partition key or the partition key along with the 
sort key/(s). It supports faster, flexible lookups without scanning the whole table.
We can create multiple GSis for different queries when necessary and I have taken 
advantage of that in this project. An example can be seen in: delete_items.py

// Reserved Keywords in DynamoDB //
'name' is an example of this. To avoid conflicts we can use expression attribute names and values
- Prepare placeholders and values to update the item's name safely, avoiding reserved word conflicts
        if name:
            update_expr.append('#name = :name')
            expr_attr_names['#name'] = 'name'
            expr_attr_values[':name'] = name

update_expr will hold the update instructions (like SET #name = :name), expr_attr_values will hold
the values to substitute (like {':name': 'New Category Name'}), and expr_attr_names will hold 
placeholder names (like {'#name': 'name'}).

// Testing //
Naming a function: test_<functionBeingTested>_<scenario>_<expectedResult>
All tests follow this structure above. One thing to note is that all test functions must start
with test_ to use pytest.
Best practice for test set up (AAA):
Arrange - set everything up you need for the test
Act - call function we are testing 
Assert - verify results 


# Future Work:
// validation.py //
Add in .strip() to required fields to stop doing .strip() in the code multiple times
to remove some of the repetitive code for better readable code.

// create_item.py //
Add in ClientError handling for the ConditionExpression error if triggered. 409 return should 
be used - this is a common error code to be thrown when you have duplicate resources.

// Adding in more ClientErrors //
I have realised when reviewing my code I have not caught ClientErrors throughout the project
as I learned about them very recently. To imporve this porject I would go back and add more
robust error handling. 

// Move critical checks earlier on //
Always check existence first before building update expressions. There is no need to waste time
parsing and validating if the item doesn’t exist. Overall it will speed up execution and avoids 
pointless computation.
Example we can look at: update_item.py the critical check happens too late

// Security //
DynamoDB encrypts by default which is great however there are some drawbacks:
It is proneto DDos attacks and attackers can floor the API with requests causing downtime and
high costs. To avoid this I would need to implement rate limits to prevent this issue. At the 
moment anyone can access the API through the links to restrict this I need to try implementing
IAM Authentication for API Gateway which would only allow certain users to make updates or I
can try to implement a Secure API Gateway with an API Key which would require a key to be passed
in heads (e.g. x-api-key) for every request. This second methods works as if it was a password
being passed in with the request.

# Lessons Learned:
// DynamoDB isn't a relational database // 
I learned to shift my thinking from normalized to denormalized, access-pattern-based design,
storing related data together (like items inside orders) to reduce the need for joins and
extra lookups.

// Global Secondary Indexes (GSIs) unlock querying flexibility //
GSIs allowed me to query using non-primary keys (e.g. querying by itemID instead of PK/SK). 
Understanding when and how to use them was essential for building features like updating or 
deleting specific items.

// Validation and early checks save compute time //
Performing critical validations (like checking if an item exists) before doing any further
processing will help streamline the logic and avoid wasting Lambda execution time.

// Decimal vs float: AWS is strict about types //
DynamoDB uses Decimal while JSON uses int/float. I had to consistently convert numeric values
safely to avoid type errors, and even used a custom DecimalEncoder for clean responses.

// Reserved keywords can cause silent failures //
Simple words like name are reserved in DynamoDB expressions. I learned to safely use
ExpressionAttributeNames and ExpressionAttributeValues to avoid unexpected behavior when
updating items.

// Good error handling improves resilience //
Implementing proper try/except blocks and catching ClientError made the app more robust.
It also helped give meaningful feedback to API users when things went wrong.

// Unit testing builds confidence in your code //
Using pytest with unittest.mock showed me the importance of test isolation. I learned how
to test my Lambda functions without making actual calls to AWS, improving both speed and safety.

// IAM permissions can silently break your functions //
Many issues (403 errors) were caused by missing permissions. I learned to carefully configure
IAM roles and policies for each Lambda function.

// Postman is a useful tool for testing APIs //
I used Postman to simulate all requests, validate responses, and debug payload issues quickly,
making it a vital part of my workflow.