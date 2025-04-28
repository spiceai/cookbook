import org.skife.jdbi.v2.sqlobject.{Bind, SqlQuery}
import org.skife.jdbi.v2.sqlobject.stringtemplate.UseStringTemplate3StatementLocator
import org.skife.jdbi.v2.{DBI, Handle}
import java.sql.{ResultSet, Timestamp}
import org.skife.jdbi.v2.StatementContext
import org.skife.jdbi.v2.tweak.ResultSetMapper
import java.util.{List => JavaList}
import scala.jdk.CollectionConverters._

case class ComponentRecord(
  RecordId: String,
  GroupId: String,
  ComponentId: String,
  ComponentTypeId: String,
  ComponentConfig: String,
  CreationTimestamp: Timestamp,
  UpdateTimestamp: Timestamp
)

@UseStringTemplate3StatementLocator
trait ComponentRecordDao {
  @SqlQuery(
    """
       SELECT RecordId, GroupId, ComponentId, ComponentTypeId, ComponentConfig, CreationTimestamp, UpdateTimestamp
       FROM addons
       WHERE RecordId = :recordId and GroupId = :groupId
       ORDER BY CreationTimestamp DESC
    """
  )
  def getComponentsByRecordAndGroup(
      @Bind("recordId") recordId: String,
      @Bind("groupId") groupId: String
  ): JavaList[ComponentRecord]

  @SqlQuery(
    """
       SELECT RecordId, GroupId, ComponentId, ComponentTypeId, ComponentConfig, CreationTimestamp, UpdateTimestamp
       FROM addons
       WHERE ComponentTypeId = :componentTypeId
       LIMIT :batchSize
    """
  )
  def getComponentsByType(
      @Bind("componentTypeId") componentTypeId: String,
      @Bind("batchSize") batchSize: Int
  ): JavaList[ComponentRecord]
}

object DemoApp {
  def main(args: Array[String]): Unit = {
    val jdbcUrl = "jdbc:arrow-flight-sql://host.docker.internal:63915?useEncryption=false"
    val username = ""
    val password = ""

    val dbi = new DBI(jdbcUrl, username, password)

    dbi.registerMapper(new ResultSetMapper[ComponentRecord] {
      override def map(index: Int, rs: ResultSet, ctx: StatementContext): ComponentRecord = {
        ComponentRecord(
          RecordId = rs.getString("RecordId"),
          GroupId = rs.getString("GroupId"),
          ComponentId = rs.getString("ComponentId"),
          ComponentTypeId = rs.getString("ComponentTypeId"),
          ComponentConfig = rs.getString("ComponentConfig"),
          CreationTimestamp = rs.getTimestamp("CreationTimestamp"),
          UpdateTimestamp = rs.getTimestamp("UpdateTimestamp")
        )
      }
    })

    val dao = dbi.onDemand(classOf[ComponentRecordDao])

    try {
      val components1 = dao.getComponentsByRecordAndGroup("record123", "group456")
      println("Components by record and group:")
      components1.asScala.foreach(println)

      val components2 = dao.getComponentsByType("type789", 10)
      println("\nComponents by component type:")
      components2.asScala.foreach(println)
    } finally {
      dbi.close(dao)
    }
  }
}
