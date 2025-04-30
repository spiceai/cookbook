import java.util.List;

import org.jdbi.v3.sqlobject.config.RegisterRowMapper;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.customizer.Bind;

@RegisterRowMapper(MessagingServiceAddOnMapper.class)
public interface MessagingServiceDao {

    @SqlQuery("SELECT * FROM addons WHERE AccountId = :accountId AND ServiceId = :serviceId")
    List<MessagingServiceAddOn> getMessagingServiceAddOns(@Bind("accountId") String accountId, @Bind("serviceId") String serviceId);

    @SqlQuery("SELECT * FROM addons WHERE AddOnTypeSid = :addOnTypeSid LIMIT :limit")
    List<MessagingServiceAddOn> getMessagingServiceAddOnByAddOnType(@Bind("addOnTypeSid") String addOnTypeSid,
                                                                    @Bind("limit") int limit);
}