import java.sql.ResultSet;
import java.sql.SQLException;
import org.jdbi.v3.core.mapper.RowMapper;
import org.jdbi.v3.core.statement.StatementContext;


public class MessagingServiceAddOnMapper implements RowMapper<MessagingServiceAddOn> {
    @Override
    public MessagingServiceAddOn map(ResultSet rs, StatementContext ctx) throws SQLException {
        MessagingServiceAddOn addOn = new MessagingServiceAddOn();
        addOn.setAccountSid(rs.getString("AccountId"));
        addOn.setMessagingServiceSid(rs.getString("ServiceId"));
        addOn.setAddOnSid(rs.getString("AddOnSid"));
        addOn.setAddOnTypeSid(rs.getString("AddOnTypeSid"));
        addOn.setAddOnJson(rs.getString("AddOnJson"));
        addOn.setDateCreated(rs.getTimestamp("DateCreated"));
        addOn.setDateUpdated(rs.getTimestamp("DateUpdated"));
        return addOn;
    }
}
