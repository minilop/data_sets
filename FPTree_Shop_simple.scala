package com.likai.spark

import org.apache.spark.mllib.fpm.FPGrowth
import org.apache.spark.sql.SparkSession

object FPTree_Shop_simple {
  def main(args:Array[String]):Unit = {

    val buyerPhone_trade = 60
    val sellerNick_trade = 73
    val created_trade = 22

    val minSupport = args(0).toDouble
    val minConfidence = args(1).toDouble
    val outRepartition = args(2).toInt
    val numPartition = args(3).toInt

    val input = args(4)
    val out1 = args(5)
    val out2 = args(6)

    val spark = Context.getContext("fptree_shop_simple")

    val sc = spark.sparkContext
    val file = sc.textFile(input)

    val temp = file.filter(line => {
      val arr = line.split("\002")
      val created = arr(created_trade).trim
      if((!arr(sellerNick_trade).contains("天猫超市"))
        && created >= "2017-04-01 00:00:00" && created <= "2017-08-31 59:59:59") true else false
    }).map(x => {
      val arr = x.split("\002")
      (arr(buyerPhone_trade).trim, arr(sellerNick_trade).trim)
    })

    //val map = temp.map(kv => {kv._2}).distinct().zipWithIndex()

    //val map_broad = spark.sparkContext.broadcast(map.collectAsMap())

    val data = temp.reduceByKey((x, y) => x + "\002" + y).map{
      case (k, v) => {
        v.split("\002").toSet[String].toArray
      }
    }.filter(arr =>{
      arr.length < 400
    })

    val fpg = new FPGrowth().setMinSupport(minSupport).setNumPartitions(numPartition)
    val model = fpg.run(data)

//    model.save(sc, out1)

    //频繁项次数
    val freqsData = model.freqItemsets.map(itemset => {
      itemset.items.mkString("\002")+" : "+itemset.freq
    })

    val confidenceData = model.generateAssociationRules(minConfidence).map(rule => {
      rule.antecedent.mkString("\002")+"->"+rule.consequent.mkString("\002")+" : "+rule.confidence
    })

    //map.map(kv => {kv._1 + "\002" + kv._2}).saveAsTextFile("/testenv/likai/sellerIndexMaps")
    freqsData.repartition(outRepartition).saveAsTextFile(out1)
    confidenceData.repartition(outRepartition).saveAsTextFile(out2)

    spark.stop()
  }
}
