import org.skife.jdbi.v2.sqlobject.{Bind, SqlQuery}
import org.skife.jdbi.v2.sqlobject.stringtemplate.UseStringTemplate3StatementLocator
import org.skife.jdbi.v2.{DBI, Handle}
import java.sql.{ResultSet, Timestamp}
import org.skife.jdbi.v2.StatementContext
import org.skife.jdbi.v2.tweak.ResultSetMapper
import java.util.{List => JavaList}
import scala.jdk.CollectionConverters._

case class MessagingServiceAddOn(
  AccountSid: String,
  MessagingServiceSid: String,
  AddOnSid: String,
  AddOnTypeSid: String,
  AddOnJson: String,
  DateCreated: Timestamp,
  DateUpdated: Timestamp
)

@UseStringTemplate3StatementLocator
trait MessagingServiceDao {
  @SqlQuery(
    """
       SELECT AccountId,ServiceId,AddOnSid,AddOnTypeSid,AddOnJson,DateCreated,DateUpdated
       FROM addons
       WHERE AccountId = :accountId and ServiceId = :serviceId
       ORDER BY DateCreated DESC
    """)
  def getMessagingServiceAddOns(
      @Bind("accountId") accountSid: String,
      @Bind("serviceId") serviceId: String
  ): JavaList[MessagingServiceAddOn]

  @SqlQuery(
    """
       SELECT AccountId,ServiceId,AddOnSid,AddOnTypeSid,AddOnJson,DateCreated,DateUpdated
       FROM addons
       WHERE AddOnTypeSid = :addOnTypeSid
       limit :batchSize
    """)
  def getMessagingServiceAddOnByAddOnType(
      @Bind("addOnTypeSid") addOnTypeSid: String,
      @Bind("batchSize") batchSize: Int
  ): JavaList[MessagingServiceAddOn]
}

object MessagingServiceApp {
  def main(args: Array[String]): Unit = {
    val jdbcUrl = "jdbc:arrow-flight-sql://localhost:50051?useEncryption=false"
    val username = ""
    val password = "123"

    val dbi = new DBI(jdbcUrl, username, password)

    dbi.registerMapper(new ResultSetMapper[MessagingServiceAddOn] {
      override def map(index: Int, rs: ResultSet, ctx: StatementContext): MessagingServiceAddOn = {
        MessagingServiceAddOn(
          AccountSid = rs.getString("AccountId"),
          MessagingServiceSid = rs.getString("ServiceId"),
          AddOnSid = rs.getString("AddOnSid"),
          AddOnTypeSid = rs.getString("AddOnTypeSid"),
          AddOnJson = rs.getString("AddOnJson"),
          DateCreated = rs.getTimestamp("DateCreated"),
          DateUpdated = rs.getTimestamp("DateUpdated")
        )
      }
    })

    val dao = dbi.onDemand(classOf[MessagingServiceDao])

    try {
      val addOns1 = dao.getMessagingServiceAddOns("account123", "service456")
      println("Add-ons by account and service:")
      addOns1.asScala.foreach(println)

      val addOns2 = dao.getMessagingServiceAddOnByAddOnType("type789", 10)
      println("\nAdd-ons by add-on type:")
      addOns2.asScala.foreach(println)
    } finally {
      dbi.close(dao)
    }
  }
}
