flask --app mfo.app users create admin@testmail.com --password abcd1234
flask --app mfo.app roles add admin@testmail.com Admin
flask --app mfo.app users activate admin@testmail.com

flask --app mfo.app users create user@testmail.com --password password
flask --app mfo.app roles add user@testmail.com User
flask --app mfo.app users activate user@testmail.com