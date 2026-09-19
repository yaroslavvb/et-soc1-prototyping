# Lab machine accounts

The AI Foundry lab machines are Ubuntu 24.04 boxes on our Tailscale tailnet:

| Machine | ET-SoC-1 devices |
|---|---|
| `aifoundry1` | 2: `/dev/et0_{mgmt,ops}`, `/dev/et1_{mgmt,ops}` |
| `aifoundry2` | 1: `/dev/et0_{mgmt,ops}` |
| `aifoundry3` | 1: `/dev/et0_{mgmt,ops}` |

The device nodes are mode 0666, so any local account can use them and no group membership is needed.
The ET tools are in `/opt/et/bin`. Each machine has its own local `/home`, so files are not shared between machines.

For people without this repo, there is a standalone version of this page with the script built in:
https://spacesheep.dev/@yaroslavvb/aifoundry-lab-accounts

## How access works

Logins go through **Tailscale SSH**, not sshd passwords or keys. The tailnet's SSH policy lets members log in
as any account that exists on the machine, after a browser check that Tailscale repeats every so often.
So a new person needs two things: membership in the tailnet, and an account on each machine.

## Adding someone

1. Get a username from them (lowercase, e.g. their usual handle). You can also ask for their SSH public key
   (`~/.ssh/id_ed25519.pub`). The key is optional: it is only a fallback for plain sshd over the LAN.
2. Make sure they are invited to the tailnet (Tailscale admin console, Users, Invite).
3. From a machine where `ssh root@aifoundry1` works, run this from the repo root:

   ```bash
   scripts/add-lab-user.sh alice ~/Downloads/alice.pub "Alice Example"
   ```

   It creates the account on every `aifoundryN` listed by `tailscale status` (set `HOSTS="aifoundry2"` to limit it),
   installs the key, and checks that the account can read and write `/dev/et*`. Re-running it is safe.
4. Send them the "First login" section below.

Accounts have no password, so they cannot use `sudo`. To give someone sudo on a machine, add them to the group
and set a password that they can change later with `passwd`:

```bash
ssh -t root@aifoundry1 'usermod -aG sudo alice && passwd alice'
```

### By hand

Run these for each machine. `adduser` asks for the full name, and the other fields can stay empty:

```bash
ssh -t root@aifoundry2 adduser --disabled-password alice
ssh alice@aifoundry2 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys' < alice.pub   # optional key
```

## First login

1. Accept the Tailscale invite and install Tailscale on your laptop.
2. Run `ssh alice@aifoundry1` (or `aifoundry2`, `aifoundry3`). If Tailscale prints a URL, open it to confirm
   it's you. Tailscale asks for this again periodically.
3. Put the ET tools on your PATH: `echo 'export PATH=/opt/et/bin:$PATH' >> ~/.bashrc`.

If Tailscale says the policy does not permit you to log in, a tailnet admin needs to add you to the SSH rules
in the tailnet policy file.
