package com.likai.labelsystem

import java.io.{BufferedWriter, File, FileWriter}

import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.clustering.{GaussianMixture, KMeans}
import org.apache.spark.ml.feature.{MinMaxScaler, PCA, PCAModel, StandardScaler}
import org.apache.spark.ml.linalg.Vectors
import org.apache.spark.sql.SparkSession

import scala.io.Source

object LabelsCluster {
  def main(args:Array[String]):Unit = {
    val spark = SparkSession.builder().master("local").getOrCreate()

    val tt = Array("","")

    val wr = new BufferedWriter(new FileWriter("/home/likai/trades.txt"))
    tt.foreach(l => {wr.write(l+'\n')})
    wr.close()

    val dataset = spark.createDataFrame(Seq(
      ("asd1", Vectors.dense(1.0, 1.0)),
      ("asd2", Vectors.dense(1.1, 1.2)),
      ("asd3", Vectors.dense(1.1, 1.0)),
      ("asd4", Vectors.dense(0.0, 0.2))
    )).toDF("id", "features")

    val standar = new StandardScaler()
    standar.setInputCol("features")
    standar.setOutputCol("scaledFeatures")
    standar.setWithMean(true)
    standar.setWithStd(true)

    val minmax = new MinMaxScaler()
    minmax.setInputCol("features").setOutputCol("scaledFeatures")

    val pca = new PCA()
        .setInputCol("scaledFeatures")
        .setOutputCol("pcaFeatures")
        .setK(3)
    //高维数据，
    val center_num = 2
    val kmeans = new KMeans().setFeaturesCol("pcaFeatures").setK(center_num).setSeed(1L).setMaxIter(20)

    val gm = new GaussianMixture().setK(3)
                  .setPredictionCol("prediction")
                  .setProbabilityCol("prob")

    val pipeline = new Pipeline().setStages(Array(standar, pca, kmeans))

    val model = pipeline.fit(dataset)

    model.write.overwrite().save("/Users/likai/models")


    //================以下为测试======================
    //new class
    val sameModel = PipelineModel.load("PipelineModel保存的路径")

    val test = spark.createDataFrame(Seq(
      ("asd11", Vectors.dense(0.0, 0.1))
    )).toDF("id", "features")

    val rs = model.transform(test)
    val rs1 = model.transform(dataset)

    val file = spark.sparkContext.textFile("/testenv/sunjingzhi/date6_12/phoneAllDataFinal")
    val trade = file.filter(l => l.split("\002")(1).contains("XXXXXXX"))


    def output(header:Array[String], data:Array[String], path:String):Unit = {
      val wr = new BufferedWriter(new FileWriter(path))

    }
  }
}
