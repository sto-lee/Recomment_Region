DROP DATABASE IF EXISTS HomeGenie;
DROP USER IF EXISTS 'GoToHome'@'%';

USE mysql;

CREATE USER 'GoToHome'@'%' identified BY 'skn1234';
CREATE DATABASE HomeGenie;

-- SHOW DATABASES;

USE HomeGenie;

GRANT ALL PRIVILEGES ON HomeGenie.* TO 'GoToHome'@'%';


CREATE TABLE District(
	district_id INT NOT NULL AUTO_INCREMENT,
	district_name VARCHAR(20) NOT NULL, 
	PRIMARY KEY (district_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='구';

CREATE TABLE RecType(
	type_id INT NOT NULL AUTO_INCREMENT,
	type_name VARCHAR(50) NOT NULL,
	type_desc TEXT NOT NULL,
	PRIMARY KEY (type_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='추천타입';

CREATE TABLE Neighborhood(
	neighborhood_id INT NOT NULL AUTO_INCREMENT,
	district_id INT NOT NULL,
	neighborhood_name VARCHAR(40) NOT NULL, 
	neighborhood_lat FLOAT NOT NULL,
	neighborhood_lon FLOAT NOT NULL,
	PRIMARY KEY (neighborhood_id),
	FOREIGN KEY (district_id) REFERENCES District (district_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='동';

CREATE TABLE Board(
	board_id INT NOT NULL AUTO_INCREMENT,
	neighborhood_id INT NOT NULL,
	board_type ENUM('free','anon') NOT NULL,
	PRIMARY KEY (board_id),
	FOREIGN KEY (neighborhood_id) REFERENCES Neighborhood (neighborhood_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='게시판';

CREATE TABLE RecProfile(
	profile_id INT NOT NULL AUTO_INCREMENT,
	neighborhood_id INT NOT NULL,
	age INT NOT NULL,
	preferred_transport JSON NOT NULL,
	preferred_amenities JSON NOT NULL,
	preferred_property_type JSON NOT NULL,
	PRIMARY KEY (profile_id),
	FOREIGN KEY (neighborhood_id) REFERENCES Neighborhood (neighborhood_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='추천 프로필';

CREATE TABLE Amenity (
	amenity_id INT NOT NULL AUTO_INCREMENT,
	neighborhood_id INT NULL,
	amenity_type1 VARCHAR(30) NOT NULL,
	amenity_type2 VARCHAR(50) NOT NULL,
	title VARCHAR(100) NULL,
	street_address VARCHAR(500) NULL,
	amenity_lat FLOAT NULL,
	amenity_lon FLOAT NULL,
	PRIMARY KEY (amenity_id),
	FOREIGN KEY (neighborhood_id) REFERENCES Neighborhood (neighborhood_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='편의시설';

CREATE TABLE Property (
	property_id INT NOT NULL AUTO_INCREMENT,
	neighborhood_id INT NULL,
	property_transaction_type VARCHAR(10) NOT NULL,
	property_room_type VARCHAR(10) NOT NULL,
	property_lat FLOAT NOT NULL,
	property_lon FLOAT NOT NULL,
	PRIMARY KEY (property_id),
	FOREIGN KEY (neighborhood_id) REFERENCES Neighborhood (neighborhood_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='매물';

CREATE TABLE User(
	user_id INT NOT NULL AUTO_INCREMENT,
	nickname VARCHAR(30) NOT NULL,
	email VARCHAR(100) NULL,
	password VARCHAR(100) NULL,
	phone_number VARCHAR(30) NULL,
	image_link TEXT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='사용자';

CREATE TABLE SocialAccount(
	social_account_id INT NOT NULL AUTO_INCREMENT,
	user_id INT NOT NULL,
	provider_type ENUM('KAKAO','GOOGLE') NOT NULL,
	social_id VARCHAR(100) NOT NULL,
	access_token TEXT NULL,
	refresh_token TEXT NULL,
	token_expires_at DATETIME NULL,
	provider_info JSON NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (social_account_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='소셜 로그인 정보';


CREATE TABLE Post (
	post_id INT NOT NULL AUTO_INCREMENT,
	board_id INT NOT NULL,
	user_id INT NOT NULL,
	title TEXT NOT NULL,
	content TEXT NOT NULL,
	view_count INT NOT NULL DEFAULT 0,
	like_count INT NOT NULL DEFAULT 0,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	modified_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
	is_deleted BOOLEAN NOT NULL DEFAULT FALSE, 
	PRIMARY KEY (post_id),
	FOREIGN KEY (board_id) REFERENCES Board (board_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='게시글';

CREATE TABLE PropertyAmenity(
	property_amenity_id INT NOT NULL AUTO_INCREMENT,
	amenity_id INT NOT NULL,
	property_id INT NOT NULL,
	PRIMARY KEY (property_amenity_id),
	FOREIGN KEY (amenity_id) REFERENCES Amenity (amenity_id),
	FOREIGN KEY (property_id) REFERENCES Property (property_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='매물 근처 편의시설';

CREATE TABLE PropertyRecommendation (
	recommendation_id INT NOT NULL AUTO_INCREMENT,
	profile_id INT NOT NULL,
	type_id INT NOT NULL,
	recommended_lat FLOAT NOT NULL,
	recommended_lon FLOAT NOT NULL,
	PRIMARY KEY (recommendation_id), 
	FOREIGN KEY (profile_id) REFERENCES RecProfile (profile_id),
	FOREIGN KEY (type_id) REFERENCES RecType (type_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='추천매물';

CREATE TABLE Comment (
	comment_id INT NOT NULL AUTO_INCREMENT,
	post_id INT NOT NULL,
	user_id INT NOT NULL,
	content TEXT NOT NULL,
	like_count INT NOT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
	reply_count INT NOT NULL,
	PRIMARY KEY (comment_id),
	FOREIGN KEY (post_id) REFERENCES Post (post_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='댓글';

CREATE TABLE CommentChild (
	comment_child_id INT NOT NULL AUTO_INCREMENT,
	comment_id INT NOT NULL,
	user_id INT NOT NULL,
	content TEXT NOT NULL,
	like_count INT NOT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY (comment_child_id),
	FOREIGN KEY (comment_id) REFERENCES Comment (comment_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='댓댓글';

CREATE TABLE PostLike (
	post_like_id INT NOT NULL AUTO_INCREMENT,
	post_id INT NOT NULL,
	user_id INT NOT NULL, 
	PRIMARY KEY (post_like_id),
	FOREIGN KEY (post_id) REFERENCES Post (post_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)	
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='게시글 좋아요';

CREATE TABLE PostBookmark (
	post_bookmark_id INT NOT NULL AUTO_INCREMENT,
	post_id INT NOT NULL,
	user_id INT NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (post_bookmark_id),
	FOREIGN KEY (post_id) REFERENCES Post (post_id),
	FOREIGN KEY (user_id) REFERENCES User (user_id)	
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='게시글 북마크';

CREATE TABLE CommentLike (
	comment_like_id INT NOT NULL AUTO_INCREMENT,
	comment_id INT NOT NULL,
	user_id INT NOT NULL, 
	PRIMARY KEY (comment_like_id),
	FOREIGN KEY (comment_id) REFERENCES Comment (comment_id), 
	FOREIGN KEY (user_id) REFERENCES User (user_id)	
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='댓글 좋아요';

CREATE TABLE CommentChildLike (
	comment_child_like_id INT NOT NULL AUTO_INCREMENT,
	comment_child_id INT NOT NULL,
	user_id INT NOT NULL, 
	PRIMARY KEY (comment_child_like_id),
	FOREIGN KEY (comment_child_id) REFERENCES CommentChild (comment_child_id), 
	FOREIGN KEY (user_id) REFERENCES User (user_id)	
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='댓댓글 좋아요';

CREATE TABLE Image (
	image_id INT NOT NULL AUTO_INCREMENT,
	post_id INT NULL,
	url TEXT NOT NULL,
	display_order INT NOT NULL,
	PRIMARY KEY (image_id),
	FOREIGN KEY (post_id) REFERENCES Post (post_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='이미지';

CREATE TABLE SearchHistory(
	search_id INT NOT NULL,
	board_id INT NULL,
	keyword VARCHAR(100) NOT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (search_id),
	FOREIGN KEY (board_id) REFERENCES Board (board_id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='검색이력';


SHOW TABLES;
