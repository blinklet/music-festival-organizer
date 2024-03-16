# Requirements

## Question

* Who pays? Is there a need to track who pays? Or do you assume the participant pays and track all payments against the participant ID?
* For groups, is pays? The teacher? Or should there be an option to identify a "contact person" for groups?
* Who creates participant profiles?

## Assumptions

Version one makes the following assumptions:

* I assume each festival will host their own database and web server. Version 1 of this program supports only one festival. This is not a web platform that can manage multiple festivals, yet.

## Workflow

### Data gathered

Data is gathered from parents, participants, and teachers via forms. Results in five import spreadsheets delivered to the scheduler:

#### Accompanists

*impt_accompanists.csv*

* Name
* Phone number
* Address

#### Groups

*impt_dancegroups.csv*

Example is for Dance Groups and is blank. No data. Fields are:

* OL_IPARTID	
* CGROUPNAME	
* CDANCERFN	
* CDANCERLN	
* DDOB	
* CPHONE

#### Participants

*impt_parts.csv*

First file. Seems to be contact information with billing info. One line per person

* Part ID
* Participant name
* Address
* Phone number
* Date of birth
* Type
* "CPART2" (ocasionally seems to include a name)
* Teacher ID
* School name
* email (usually a teacher or parent email)
* Request (usually about scheduling restrictions, who to contact, or how to bill)
* Fee
* Amount paid

#### Registrations

* impt_parts2.csv*

Second file, assume OLPID matches "Part ID" from first file. Multiple lines per person, if they signed up for more than one class

* "OLPID"
* Class entry #
* Class name
* Accompanist name
* Music piece (Up to 5, usually only 1)
* Length of each piece (in minutes)
* Composer of each piece
* Class fee (not clear why this is sometimes different from "Fee", above)
* paid flag

#### Teachers

*impt_teachers.csv*

* Teacher ID #
* Name
* Address
* Phone number
* Email address


### Data issues

The Registrations

Length of piece is manually entered by participant and is not trusted. Scheduler manually changes it to include the time per person + time of repertoire.

Scheduler cross-checks total fees paid with e-transfers received to see if everyone paid

### Roll over to a new year

The Roll over 2018 is how we move from one year to another, so far it works.

## User stories

The users are:

* Admin
* Teacher (represents school) (may take role of participant when registering a group)
* Guardian (info only) (may take role of participant if registering child on their behalf)
* Participant (may be an individual or a group) (needs a guardian if a minor)

### Admin

The Admin does the following:

* Build the syllabus
  * Create classes in the system
* Register adjudicators
  * Add adjudicator info into the system (check for near-duplicates)
* Register parts
  * Create a list of music pieces, with composer name and length (check for near-duplicates)
  * Assign pieces to classes (if recommended lists are available)
* May "Freeze" the system to stop changes, when deadline is passed

### Teacher

* Create their own profile in the system
* Register Accompanists in the system  (search first, check for near-duplicates)
* Registers Schools in the system (search first, check for near-duplicates)

* May register participant profiles in the system (individuals or groups)
* May identify themselves as an accompanist

### Participants

* Key = ID # (used to link profiles, if needed)
* May be in individual or a group
* Create their own profile in the system (check if one already created by guardian or teacher)
* Register guardian profile in the system (check if one already created by guardian or teacher)

### Guardian

* Create their own profile in the system (check if one already created by participant or teacher)
* Register participant profile in the system (check if one already created by participant or teacher)
* See "participant" for other tasks

## Data

### Admin

Enters data into system where needed, such as venue information, session information, etc...  Runs reports and uses them to build the festival schedule

Manages data backup. Activates yearly rollover.

* Account info

Creates the music festival profile
* Name
* Logo
* Address
* Phone number
* Dates



### Teacher

Profile of teacher. Teachers can log in and create or update their profiles.

* Linked to participant
* May see participant names of those linked to their profile
* May identify themselves as an accompanist

* ID #
* Name
* School
* Contact information
* Billing information
* Accompanist?
* Linked profiles (may be participant (group or individual))

### Participant

Profile of participant. Participants can log in and create or update their profiles. Include parent names for payment

* May be linked to accompanist, group, teacher,
 and/or guardian
* May see teacher names linked to their profile
* May see group names linked to their profile

* Account info
* First Name, Last Name
* Address
* Date of Birth
* Gender
* Phone Number
* email address
* Guardian ID (if a minor) (may be null)
* Linked profiles (may be group (another ))
  * WARNING: Participant may have more than one teacher related to different registrations (example: a Piano teacher and a Voice teacher)
  * How to handle multiple teachers with registrations????
* School ID
* Amount paid
* Request (like, "Katie has a Bluefield Band Trip April 25-27.")

### School

* School ID
* School Name
* Address
* Phone number
* School info (any text)


### Guardian

May be needed if parent signs up participant, instead of teacher.
May also be needed for payment of participant is a minor.

* Linked to participant

* Account info
* Name
* Contact information

* Carry over from previous year, if they exist. 
* Add and delete guardian record.
* Change guardian information, like contact info

### Adjudicator

Profile of adjudicator. They are a resource assigned to sessions. Probably, one of the "users" will add the adjudicator profiles.

* Linked to classes or sessions

* Name
* Contact information

* Carry over from previous year, if they exist. 
* Add and delete adjudicators.
* Change adjudicator information, like contact info

### Accompanist

Profile of accompanist. They are a resource assigned to sessions. Probably, one of the "users" will add the accompanist profiles so they can be selected. It may be that "teacher", "parent", or "participant" will enter the accompanist profile if it does no already exist.

* Linked to registrations, not to teachers or participants

* Name
* Phone number
* e-mail address

* Carry over from previous year, if they exist. 
* Add and delete accompanists.
* Change accompanist information, like contact info

### Venue

Profile of hall. It is a resource assigned to sessions. Probably, one of the "users" will add the venue profiles.

* Venue name
* Address (including room number)
* Availability dates/times (?)

* Carry over from previous year, if they exist. 
* Add and delete venues.
* Change venue information, like avaiability

### Music part

Profile of a piece of music. Include length of music. It would be helpful to have this pre-populated so it can be selected in the registration form. Probably, one of the "users" will add the Music part profiles.

* Carry over from previous year, if they exist. 
* Add and delete parts.
* Identify if "accompanist required" (helps find registrations without an accompanist when scheduling)

### Session or class

Sessions, or classes, are already created by a "user" and are available to register for. 

* Class info
  * Class name
  * Class #
  * Start time
  * Duration
  * List of recommended music parts
  * Cost

### Registration

A entry for each registration (an association table)

* Class #
* participant ID #
* Music part #1, #2, etc...
  * May be a part ID # (from list of pre-registered pieces) (5 slots available, or JSON list object), or
  * May be part ID = NULL, fill in custom part field (5 slots available)
* Accompanist ID #
* Who will pay
  * Participant
  * Parent (linked)
  * Teacher (linked)
  * Group (linked)
* Fees are tracked under class ID. participant ID 
  * Can be rolled up under guardian or teacher (each of whom may represent multiple participants)

* Not carried over from previous year

## Reports

### Fee report by participant

(see *Total Fees.pdf*)
A table showing:

* For each participant
    * Class reistrations (may be more than one)
        * Class registered in
        * Fee for class
        * Who pays for registration
    * Total of all fees
    * Total fees paid
    * Notes
  
### Fee report by payer

Sames as above, except for each person identified as a payer:

* For each payer
    * Class reistrations (may be more than one)
        * Class registered in
        * Participant name
        * Fee for class
    * Total of all fees
    * Total fees paid
    * Notes

### Preliminary Program Report

(see *Preliminary Program.pdf*)

One report per session? Specify which Session type (e.g.: Voice), Date, Session time (e.g.:Morning, Afternoon, Evening)

* Header
  * Day and Date of session
  * Session type (e.g.: Voice)
  * Venue name
  * Adjudicator Name
* A table showing:
  * Class start time
  * Class #
  * Class Name
    * ____ #. (each participant's order in the program)
    * Participant Name (0 or more participants per class)
    * Music Part name - Composer Name (1 or more parts per participant)

### Class summary

List all classes

(see *parts_sumbyclassno.pdf*)

* A table showing:
  * Class #
  * Class Name
    * Participant Name (0 or more participants per class)
      * Music Part name - Composer Name (1 or more parts per participant)
      * Length of part

### Adjudicator Report

(see *Voice program.pdf*)

Specify Adjudicator name, which provides list of assigned sessions. Select session and run report

* Header
  * Name of festival
  * Name of Adjudicator
* Table of:
  * Class Date
  * Session (Morning, Afternoon, Evening)
  * Start Time
  * Session Code
  * Venue Name

