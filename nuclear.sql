CREATE DATABASE  IF NOT EXISTS `nuclear` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `nuclear`;
-- MySQL dump 10.13  Distrib 8.0.18, for Win64 (x86_64)
--
-- Host: localhost    Database: nuclear
-- ------------------------------------------------------
-- Server version	5.7.28-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alljobstable`
--

DROP TABLE IF EXISTS `alljobstable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alljobstable` (
  `jobid` int(11) NOT NULL AUTO_INCREMENT,
  `receivetime` varchar(45) DEFAULT NULL,
  `endtime` varchar(45) DEFAULT NULL,
  `jobtype` varchar(45) DEFAULT NULL,
  `username` varchar(45) DEFAULT NULL,
  `jobstatus` tinyint(4) DEFAULT NULL,
  `fileaddress` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`jobid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alljobstable`
--

LOCK TABLES `alljobstable` WRITE;
/*!40000 ALTER TABLE `alljobstable` DISABLE KEYS */;
INSERT INTO `alljobstable` VALUES (1,'2019/12/31/14:35','2019/12/31/15:00','图像校准','youhengchan',1,'/data/media/pic1.tiff'),(2,'2020/1/1','2020/1/1','紧急疏散','youhengchan',0,'/data/media/pic2.tiff'),(3,'2020/1/1/0:0','2020/1/1/0:0','写项目','youhengchan',0,'/data/media/pic3.tiff'),(4,'2020/1/2','2020/1/2','测试导出','admin',1,'/data/media/pic4.tiff');
/*!40000 ALTER TABLE `alljobstable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `companiestable`
--

DROP TABLE IF EXISTS `companiestable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companiestable` (
  `companyname` varchar(100) NOT NULL,
  PRIMARY KEY (`companyname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `companiestable`
--

LOCK TABLES `companiestable` WRITE;
/*!40000 ALTER TABLE `companiestable` DISABLE KEYS */;
INSERT INTO `companiestable` VALUES ('湖南大学');
/*!40000 ALTER TABLE `companiestable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobtypestable`
--

DROP TABLE IF EXISTS `jobtypestable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jobtypestable` (
  `jobtype` varchar(100) NOT NULL,
  `jobcode` varchar(45) DEFAULT NULL,
  `jobdesc` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`jobtype`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobtypestable`
--

LOCK TABLES `jobtypestable` WRITE;
/*!40000 ALTER TABLE `jobtypestable` DISABLE KEYS */;
INSERT INTO `jobtypestable` VALUES ('紧急撤离','JJCL','紧急撤离，指在危险情况下人们以逃命为目的快速运动形式。');
/*!40000 ALTER TABLE `jobtypestable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userjobstable`
--

DROP TABLE IF EXISTS `userjobstable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userjobstable` (
  `jobid` int(11) NOT NULL,
  `receivetime` varchar(45) DEFAULT NULL,
  `endtime` varchar(45) DEFAULT NULL,
  `jobtype` varchar(45) DEFAULT NULL,
  `username` varchar(45) DEFAULT NULL,
  `jobstatus` tinyint(4) DEFAULT NULL,
  `fileaddress` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`jobid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userjobstable`
--

LOCK TABLES `userjobstable` WRITE;
/*!40000 ALTER TABLE `userjobstable` DISABLE KEYS */;
/*!40000 ALTER TABLE `userjobstable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userstable`
--

DROP TABLE IF EXISTS `userstable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userstable` (
  `username` varchar(45) NOT NULL,
  `password` varchar(45) DEFAULT NULL,
  `company` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userstable`
--

LOCK TABLES `userstable` WRITE;
/*!40000 ALTER TABLE `userstable` DISABLE KEYS */;
INSERT INTO `userstable` VALUES ('admin','admin','湖南大学'),('youhengchan','youhengchan@qq.com','IdioSpace Technology');
/*!40000 ALTER TABLE `userstable` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-01-02 11:31:56
