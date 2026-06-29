# postgresql.conf
path_conf = "/etc/postgresql/17/main/postgresql.conf"
with open(path_conf, "r") as f:
    lines = f.readlines()

# Filter out our previous invalid attempt and other listen_addresses settings
new_lines = [l for l in lines if "listen_addresses" not in l]
new_lines.append("\nlisten_addresses = '*'\n")

with open(path_conf, "w") as f:
    f.writelines(new_lines)

# pg_hba.conf
path_hba = "/etc/postgresql/17/main/pg_hba.conf"
with open(path_hba, "r") as f:
    hba_lines = f.readlines()

# Filter out previous scram-sha-256 attempts to keep it clean
new_hba_lines = [l for l in hba_lines if "0.0.0.0/0" not in l]
new_hba_lines.append("\nhost all all 0.0.0.0/0 scram-sha-256\n")

with open(path_hba, "w") as f:
    f.writelines(new_hba_lines)

print("Configuración de PostgreSQL corregida con éxito.")
