# terraWallet
terraWallet is a virtual wallet web application designed to put you in control of your finances. You can easily send and receive money and deposit funds from your credit or debit card. terraWallet allows users to effortlessly monitor their incoming and outgoing transactions and manage their wallets and cards, providing detailed financial information to help you get the best experience.

The project is developed using the FastAPI framework for the backend, along with SQLAlchemy for managing the database. We've adhered to the original FastAPI structure to ensure optimal performance and maintainability. We've also used third-party APIs to facilitate the authentication process.

On the frontend, we've used Next.js, a React framework, to build the application entirely from scratch without using any templates. We've also used Tailwind CSS to style the frontend components.

### You can access terraWallet at - https://terrawallet.eu

## Features

- **User Authentication**: terraWallet has two types of authentication: email and password, and Google OAuth. Users can sign up using their email and password or Google account. Cookies are used to maintain the user's session.
- **Email Verification**: Users are required to verify their email address before they can log in. An email with a verification link is sent to the user's email address.
- **Phone Verification**: Users are required to verify their phone number before they can deposit funds. A verification code is sent to the user's phone number.
- **Card Management**: Users can add multiple credit/debit cards to their account and manage them.
- **Wallet Management**: Users can create multiple wallets with different type of currencies and manage them. They can also deposit/withdraw funds to/from their wallets.
- **Category Management**: Users can create multiple categories and assign them to their transactions so they can easily track their expenses.
- **Transaction History**: Users can view their transaction history, including the amount, date, and type of transaction.
- **Recurring Transactions**: Users can set up recurring transactions that will be automatically executed at a specified interval. They are handled by using cron jobs.

## Technologies Used
- **Backend**: FastAPI, Async, SQLAlchemy, PostgreSQL, Pydantic, Pytest, JWT, Google OAuth, APScheduler, Twilio, SMTP, Docker
- **Frontend**: Next.js, Tailwind CSS, TypeScript

## Project Screenshots
- Landing page. Users can sign up or log in.
![Landing Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250336332878708757/image.png?ex=666a91f3&is=66694073&hm=80fd158b4b22b6f5bab70cd1585c43f84b39bfcd53aabda3a1f6e84c434819ae&)
- Login page. Users can log in using their email and password or Google account.
![Login Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250336546700394528/image.png?ex=666a9226&is=666940a6&hm=99ec0d64199b923eb96518274e727b4672948c2b80d56e63f5ee1638e60978f9&)
- Register page. Users can get started by creating an account and unlocking the full potential of the application.
![Register Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250336665487015998/image.png?ex=666a9243&is=666940c3&hm=0cbfdf7ae203131307ef30387ae0b49b03568332f4d102f9198da5c375f9f8aa&)
- Verification page. Users are required to verify their email address before they can log in.
![Verification Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250336838930010143/image.png?ex=666a926c&is=666940ec&hm=0ef8bb23ebb9f87f0b0cff84c31b427c2b4d9d00844bd7462206c1b0ff79a1c7&)
- Home page. Users can access the rest of the application's features through the navigation bar, such as their profile, dashboard etc.
![Home Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250337074645569577/image.png?ex=666a92a4&is=66694124&hm=1be2cd969922a13154d9eb294ef3040e83ee714b6a1f3619503b041e3d75cf54&)
- Profile page. Users can view their profile information, add a phone number, and manage their contacts. Contact list can be filtered by email address or phone.
![Profile Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250337495703621672/image.png?ex=666a9309&is=66694189&hm=53c81fa322f5775a2d811862ec129e1a866e38165aa6a10a6092d5f6a638b60e&)
- Dashboard page. Users can access their wallets, cards, categories, and transactions.
![Dashboard Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250337699496464444/image.png?ex=666a9339&is=666941b9&hm=9fa6bb5379b24d3c12cf6a42c4431a7cd8d86cf5d3c484958b58f1ce928b0823&)
- Wallets page. Users can create multiple wallets with different type of currencies and manage them.
![Wallets Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250338138073862176/image.png?ex=666a93a2&is=66694222&hm=fa8d1417a216b1a07457f3ed240237c5ba301bc23038ccaef7f8e06d0fdae137&)
- Cards page. Users can add multiple credit/debit cards to their account and manage them.
![Cards Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250338488319213601/image.png?ex=666a93f5&is=66694275&hm=2146c389a84a030faae015ef056e7682f95d79e66ba0678e35a540cee83c4931&)
- Transactions page. Users can view their transaction history, including the amount, date, and type of transaction. Category and card can be selected for each transaction from the dropdown menu.
![Transactions Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250339771457212516/image.png?ex=666a9527&is=666943a7&hm=87343e4d9accfcec7d98de2f193f36be0f2a886f47120eccd575759d6cfb12d7&)
- Categories page. Users can create multiple categories and assign them to their transactions so they can easily track their expenses.
![Categories Page](https://cdn.discordapp.com/attachments/1227194517879521374/1250338628719218770/image.png?ex=666a9417&is=66694297&hm=3c13b429915332ef5da848b0969dda1eec7fb12ac50c13d5ebe885dcaad3a77a&)
- Admin Panel. Admins can manage users such as blocking/unblocking them, viewing their details, and deactivating their accounts. Users can be filtered by their email address or phone.
![Admin Panel](https://cdn.discordapp.com/attachments/1227194517879521374/1250339581929324604/image.png?ex=666a94fa&is=6669437a&hm=248e0916b5d03492a5aa6550da661f0a64b5a91f4c7479e391aa75be1cc24a0e&)

## Database Diagram
A detailed database diagram is included to help you understand the relationships between the tables and the structure of the database.
![Database Diagram](https://cdn.discordapp.com/attachments/1227194517879521374/1250387626092007435/image.png?ex=666ac1b9&is=66697039&hm=1ed401639ac196f78d2616a7d25312f8eae73ab1c5f28f75b17007ba22f55b51&)

## Contributors

|       Name            |                   Github Username                 |
|:---------------------:|:-------------------------------------------------:|
| Alexander Videnov     | [AlexVidenov1](https://github.com/AlexVidenov1)   |
| Konstantin Ivanov     | [dnrubinart](https://github.com/dnrubinart)       |
| Radostin Mihaylov     | [radoooo11](https://github.com/radoooo11)         |