Alexa Skill to retrieve scheduled movies at a Pathe' Cinema in Netherlands.

The following cinema are supported (Amsterdam): City, De Munt, Arena.

## TODO

- Add support for other cities
- Remove weird characters and useless stuff from movie title
- Add better error handling support

## Packaging

I've followed this page http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html in order to creare the deployment package.

Remember to replace the applicationId inside lambda_handler (app.py) with your application id.
Execute these commands

- mkdir alexa_package
- pip install bs4 -t alexa_package/
- chmode u+x build.sh

and then invoke ./build.sh

## How to use it

#### Alexa ask cinema what is the schedule for city
what is the schedule for {Cinema}

#### Alexa ask cinema what is the schedule for city tomorrow
what is the schedule for {Cinema} {Day}

#### Alexa ask cinema which movies are projecting at city
which movies are projecting at {Cinema}

#### Alexa ask cinema which movies are projecting at city tomorrow
which movies are projecting at {Cinema} {Day}
