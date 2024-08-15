<h1 align="center"><img src="https://imgur.com/CVzEcBx.png" width="128"><br/>terraWallet</h1>

**terraWallet** is a virtual wallet web application designed to put you in control of your finances. You can easily send and receive money and deposit funds from your credit or debit card. terraWallet allows users to effortlessly monitor their incoming and outgoing transactions and manage their wallets and cards, providing detailed financial information to help you get the best experience.

The project is developed using the FastAPI framework for the backend, along with SQLAlchemy for managing the database. We've adhered to the original FastAPI structure to ensure optimal performance and maintainability. We've also used third-party APIs to facilitate the authentication process.

On the frontend, we've used Next.js, a React framework, to build the application entirely from scratch without using any templates. We've also used Tailwind CSS to style the frontend components.

The frontend repository can be found [here](https://github.com/Web-Team-Project/Virtual-Wallet-FE).

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
- **Backend**: FastAPI, Asynchronous, Alembic, SQLAlchemy, PostgreSQL, Pydantic, Pytest, JWT, Google OAuth, APScheduler, Twilio, SMTP, CI pipeline, Docker
- **Frontend**: Next.js, Tailwind CSS, TypeScript

## Hosted On
The project is hosted on Render, a cloud platform that makes it easy for developers to deploy web applications. You can access the application using the following links:
- [Backend](https://virtual-wallet-87bx.onrender.com)
- [Frontend](https://terrawallet-fe.onrender.com)

## Project Screenshots
- Landing page. Users can sign up or log in.
![Landing Page](https://i.imgur.com/pneQdIc.png)
- Login page. Users can log in using their email and password or Google account.
![Login Page](https://i.imgur.com/JG0xAqH.png)
- Register page. Users can get started by creating an account and unlocking the full potential of the application.
![Register Page](https://i.imgur.com/OzdPaXP.png)
- Verification page. Users are required to verify their email address before they can log in.
![Verification Page](https://i.imgur.com/5tI2IV7.png)
- Home page. Users can access the rest of the application's features through the navigation bar, such as their profile, dashboard etc.
![Home Page](https://i.imgur.com/SSgHyaR.png)
- Profile page. Users can view their profile information, add a phone number, and manage their contacts. Contact list can be filtered by email address or phone.
![Profile Page](https://i.imgur.com/MFIcvUk.png)
- Dashboard page. Users can access their wallets, cards, categories, and transactions.
![Dashboard Page](https://i.imgur.com/2dhAsmC.png)
- Wallets page. Users can create multiple wallets with different type of currencies and manage them.
![Wallets Page](https://i.imgur.com/AVvy7gk.png)
- Cards page. Users can add multiple credit/debit cards to their account and manage them.
![Cards Page](https://i.imgur.com/DqZ1yN2.png)
- Transactions page. Users can view their transaction history, including the amount, date, and type of transaction. Category and card can be selected for each transaction from the dropdown menu.
![Transactions Page](https://i.imgur.com/r77cPt7.png)
- Categories page. Users can create multiple categories and assign them to their transactions so they can easily track their expenses.
![Categories Page](https://i.imgur.com/Viuremo.png)
- Admin Panel. Admins can manage users such as blocking/unblocking them, viewing their details, and deactivating their accounts. Users can be filtered by their email address or phone.
![Admin Panel](https://i.imgur.com/nepkIwI.png)

## Database Diagram
A detailed database diagram is included to help you understand the relationships between the tables and the structure of the database.
![Database Diagram](https://i.imgur.com/UHVmfSg.png)

## Contributors

|       Name            |                   Github Username                 |
|:---------------------:|:-------------------------------------------------:|
| Alexander Videnov     | [AlexVidenov1](https://github.com/AlexVidenov1)   |
| Konstantin Ivanov     | [dnrubinart](https://github.com/dnrubinart)       |
| Radostin Mihaylov     | [radoooo11](https://github.com/radoooo11)         |