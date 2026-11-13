# LDAP hand-build

Create `LDAP-lab-stubbornpackets-uid` by hand in the ISE GUI. The pinned CiscoDevNet/ise 0.4.1 provider has no LDAP identity-source resource. The YAML name equals the ISE name. No mapper.

The object is documented in `policy/ldap.yaml`. The reader emits a placeholder module call in `environments/lab/ldap.tf`. Do not hand-edit that file. Ids stay out of `policy/`. Bind password stays outside the repo.

## Before you start

- Lab ISE 3.3 patch 1, Network Access only.
- You have an admin account that can create external identity sources.
- The OpenLDAP (or equivalent) server is reachable from the ISE node on the port you will use.
- You have the bind DN and bind password. The password is not in `policy/ldap.yaml` and must not be committed.

## GUI steps

1. Log in to the ISE admin GUI.
2. Go to Administration → Identity Management → External Identity Sources → LDAP.
3. Click Add.
4. Set the name to exactly `LDAP-lab-stubbornpackets-uid`. Description can match the YAML row. State enabled.
5. Connection:
   - Host: the lab OpenLDAP hostname or IP (fill locally; do not commit it if it is sensitive).
   - Port: 389 (or the port you actually use).
   - Secure connection: leave disabled unless you have already arranged TLS and a trust certificate.
6. Directory:
   - Base DN: `dc=lab,dc=stubbornpackets,dc=com` (or the real base DN for your lab).
   - Bind DN: `cn=ise-bind,ou=Services,dc=lab,dc=stubbornpackets,dc=com` (or the account you created for ISE).
   - Bind password: enter it in the GUI only. Do not paste it into any file in the repo.
7. Subject (user) search:
   - User search base: `ou=People,dc=lab,dc=stubbornpackets,dc=com`
   - Subject object class: `inetOrgPerson`
   - Subject name attribute: `uid`
8. Group search:
   - Group search base: `ou=Groups,dc=lab,dc=stubbornpackets,dc=com`
   - Group object class: `posixGroup`
   - Group map attribute: `memberUid`
   - Subjects in groups stored as: username (the uid value, not the DN). This matches posixGroup + memberUid.
9. Save. Confirm the object appears in the list under the exact name.
10. Optional: test the connection and a subject lookup from the GUI before you reference the name from an ISS or authentication rule.

## After the object exists

- The name can be used from `policy/identity-source-sequences.yaml` and from authentication rules.
- Run `python3.12 scripts/drift.py --environment lab` (or the matching environment). The LDAP family is not yet compared by the drift script; the name simply needs to exist for the rules that reference it.
- Do not put the UUID in `policy/` or `inventory/`.
- When a future provider release adds an `ise_ldap` resource, replace the skeleton module and re-import or recreate under the same name. Until then the GUI object is the source of truth for this one family.

## What this does not do

- Does not create the object via Terraform.
- Does not store the bind password in the repo.
- Does not enable any policy set.
- Does not invent a stage or prod environment.