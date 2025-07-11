# AnswerKing-AWS-DynamoDB

Key Points:
// DynamoDB processes number using Decimal, JSON uses int/float they are not compatible //
DynamoDB works with numbers using a Decimal format. Therefore, as a safety feature 
I have converted numbers to string first, followed by Decimal to make sure the 
format is correct and safe to use without causing errors.




TO DO LIST:
// validation.py //
Add in .strip() to required fields to stop doing .strip() in the code multiple times
to remove some of the repetitive code for better readable code.

// create_item.py //
Add in ClientError handling for the ConditionExpression error if triggered. 409 return should 
be used - this is a common error code to be thrown when you have duplicate resources.