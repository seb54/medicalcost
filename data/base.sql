CREATE TABLE SEX(
   id_sex INTEGER PRIMARY KEY AUTOINCREMENT,
   sex_type VARCHAR(50)
);

CREATE TABLE SMOKING(
   id_smoking_status INTEGER PRIMARY KEY AUTOINCREMENT,
   smoking_status VARCHAR(50)
);

CREATE TABLE REGION(
   id_region INTEGER PRIMARY KEY AUTOINCREMENT,
   region_name VARCHAR(50)
);

CREATE TABLE USER_TYPE(
   id_user_type INTEGER PRIMARY KEY AUTOINCREMENT,
   type_name VARCHAR(50)
);

CREATE TABLE PATIENT(
   id_patient VARCHAR(50),
   age INT,
   nb_children INT,
   bmi DECIMAL(15,2),
   insurance_cost DECIMAL(15,2),
   id_region INT NOT NULL,
   id_smoking_status INT NOT NULL,
   id_sex INT NOT NULL,
   PRIMARY KEY(id_patient),
   FOREIGN KEY(id_region) REFERENCES REGION(id_region),
   FOREIGN KEY(id_smoking_status) REFERENCES SMOKING(id_smoking_status),
   FOREIGN KEY(id_sex) REFERENCES SEX(id_sex)
);

CREATE TABLE USER_ACCOUNT(
   id_user_account INTEGER PRIMARY KEY AUTOINCREMENT,
   username VARCHAR(50) UNIQUE NOT NULL,
   email VARCHAR(100),
   password_hash VARCHAR(255) NOT NULL,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   id_user_type INT NOT NULL,
   FOREIGN KEY(id_user_type) REFERENCES USER_TYPE(id_user_type)
);

CREATE TABLE manages(
   id_patient VARCHAR(50),
   id_user_account INT,
   PRIMARY KEY(id_patient, id_user_account),
   FOREIGN KEY(id_patient) REFERENCES PATIENT(id_patient),
   FOREIGN KEY(id_user_account) REFERENCES USER_ACCOUNT(id_user_account)
);
