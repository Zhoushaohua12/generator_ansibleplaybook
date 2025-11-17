---
- name: Test Interactive
  hosts: localhost
  gather_facts: yes
  tasks:
    - name: Debug message
      debug:
        msg: "Running Test Interactive"