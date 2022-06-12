psql postgres -c "revoke connect on database instagram_insights from public;"
psql postgres -c "SELECT
                    pg_terminate_backend(pid)
                  FROM
                    pg_stat_activity
                  WHERE
                    pid <> pg_backend_pid()
                    AND datname = 'instagram_insights'
                  ;"
psql postgres -c "drop database if exists instagram_insights;"
psql postgres -c "drop role if exists instagram_insights;"
psql postgres -c "create database instagram_insights;"
psql postgres -c "grant connect on database instagram_insights to public;"

psql instagram_insights -c "create role instagram_insights;"
psql instagram_insights -c "alter role instagram_insights with login;"
psql instagram_insights -c "alter role instagram_insights with password 'instagram_insights';"
psql instagram_insights -c "grant all privileges on database instagram_insights to instagram_insights;"
psql instagram_insights -c "alter role intagram_insights superuser;"

psql instagram_insights -c "alter role instagram_insights set client_encoding to 'utf8'"
psql instagram_insights -c "alter role instagram_insights set timezone to 'UTC'"
# fixme
