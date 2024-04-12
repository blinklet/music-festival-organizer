# Development plan

0) Start with importing from the Excel file.

Because this is where they feel the pain right now and because creating a new sign-up experience will be a big change for users.

1) Account creation

* Login window
* New user account form (userid, password)
  * Choose role(s) when creating or updating profile
    * Key role, for now, is "scheduler"
    * Other roles not needed for importing and reporting
      * (Maybe put them in form as "greyed out")

2) Add user profile

Create model for profile, linked to each user ID
https://blog.appseed.us/how-to-use-flask-security-too-into-a-flask-project/


2) Data entry for scheduler

* Import spreadsheet

  a) Step 1: Read in and create unique profiles from spreadsheet
  b) Step 2: How to read in columns where many columns have the same name?
  c) For small ensembles, add extra participants in profiles if they do not already exist there







x) Other roles

After logged in, create, edit, or view profile info
* teacher profile
  * may create a group profile and link to it
  * may create a school profile and link to it
  * may create a contact profile and link to it
  * may 
* participant profile (individual or group)
  * may be linked to, and/or created by, a teacher
* contact profile
  * may be a parent, or group leader
  * may be linked to, and/or created by, a teacher
  * may create a group and link to it
  * may create a school and link to it

