#!/bin/bash
while read line
 do echo "rm -rf /var/qgrp/mqueue/smtp/qf/qf$line && rm -rf /var/qgrp/mqueue/smtp/df/df$line"
done

