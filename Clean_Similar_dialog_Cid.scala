package com.likai.recommender

import com.likai.spark.Context
import org.apache.spark.rdd.RDD

object Clean_Similar_dialog_Cid {

  val SPLIT = "\002"

  val phoneIndex = 47
  val cidIndex = 4
  val sumIndex = 19

  def main(args:Array[String]):Unit = {
    val input_order = args(0).trim
    val out_phone_count = args(1).trim
    val out_similar = args(2).trim
    val num = args(3).trim.toInt
    val parallel = args(4).trim

    val spark = Context.getContext("based_cid", parallelism=parallel,
      msg_maxSize="512", driver_maxResultSize="1g")
    val sc = spark.sparkContext

    val user_rdd = sc.textFile(input_order).map(line => {
      val array = line.split(SPLIT)
      val phone = array(phoneIndex).trim
      val cid = array(cidIndex).trim
      val count = 1 //array(sumIndex).trim.toInt
      (phone, cid, count)
    }).filter(kv => kv._1 != "" && kv._2 != "").map(kv => {
      (kv._1 + SPLIT + kv._2, kv._3.toDouble)
    }).reduceByKey(_+_).map(kv => {
      val arr = kv._1.split(SPLIT)
      (arr(0), arr(1), kv._2)
    }).filter(f => f._3 > 1.0).map(t => (t._1, t._2.toLong, t._3))

    val similar = cosine(user_rdd) // item1, item2, similar

    similar.map(t => {
      t._1 + SPLIT + t._2 + SPLIT + t._3
    }).repartition(num).saveAsTextFile(out_similar)

    user_rdd.map(t => {
      t._1 + SPLIT + t._2 + SPLIT + t._3
    }).repartition(num).saveAsTextFile(out_phone_count)
  }

  /**
    * user_rdd: 用户,cid,次数
    * @param user_rdd
    * @return cid1 cid2 相似度
    */
  def cosine(user_rdd:RDD[(String, Long, Double)]):RDD[(Long, Long, Double)] = {

    // to (用户, (物品，次数))
    val user = user_rdd.map(i => {
      (i._1, (i._2, i._3))
    }).sortByKey()

    // to (用户, (物品1, 次数1), (物品2, 次数2))
    val join_rdd = user.join(user)

    //re-map 同一个用户下的: ((物品1,物品2),(次数1,次数2))
    val num = join_rdd.map(f=> {
      ((f._2._1._1, f._2._2._1),(f._2._1._2, f._2._2._2))
    }).filter(kv => kv._1._1 <= kv._1._2) //取一半

    // to 同一个用户下的: ((物品1,物品2),次数1*次数2) reduce 所有用户的　次数相加
    val mul = num.map(f => {
      (f._1, f._2._1*f._2._2)
    }).reduceByKey(_+_)

    val maindiag = mul.filter(i => {i._1._1 == i._1._2})
    //对角线外其他  \sum_u(Item1_u * Item2_u)
    val elsemaindiag = mul.filter(i => {i._1._1 != i._1._2})

    //(物品1, ((物品1,物品2), 相乘结果) )
    // 还会有一个对称的　(物品2, ((物品2,物品1), 相乘结果) )
    val dot = elsemaindiag.map(f => {
      (f._1._1, (f._1._1, f._1._2, f._2))
    })
    // (物品1, 相乘结果)
    val mod = maindiag.map(f => {
      (f._1._1, f._2)
    })

    // (物品1, (物品1,其他另一个物品, 点乘结果), 物品1的mod)
    //
    val x = dot.join(mod)

    // (物品1, (物品1,其他另一个物品, 点乘结果), 物品1的mod) =>
    // (其他另一个物品, (物品1, 其他另一个物品, 点乘结果, 物品1的mod))
    val x_new = x.map(f => {
      (f._2._1._2, (f._2._1._1, f._2._1._2, f._2._1._3, f._2._2))
    })

    // {其他另一个物品, [(物品1, 其他另一个物品, 点乘结果, 物品1的mod), 其他另一个物品的mod]}
    val aa = x_new.join(mod)

    // (物品1, 其他另一个物品, 点乘结果, 物品1的mod, 其他另一个物品的mod)
    val bb = aa.map(f => {
      (f._2._1._1,f._2._1._2,f._2._1._3,f._2._1._4,f._2._2)
    })

    // 相乘结果 / sqrt(物品自相乘结果*elses相乘结果)
    val rs = bb.map(f => {
      (f._1, f._2, (f._3 / math.sqrt(f._4 * f._5)))
    })
    rs
  }
}
