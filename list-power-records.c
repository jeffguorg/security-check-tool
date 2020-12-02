#include <utmp.h>
#include <stdio.h>
#include <string.h>

int main() {
    int ret = 0;
    if((ret = utmpname("/var/log/wtmp")) != 0) {
        perror("failed to read wtmp file");
        return -1;
    }
    
    struct utmp *ent;
    while((ent = getutent()) != nullptr) {
        if((strcmp(ent->ut_user, "reboot") == 0) || (strcmp(ent->ut_user, "shutdown") == 0)) {
            printf("%s|%s|%d\n",
                    ent->ut_user,
                    ent->ut_host,
                    ent->ut_tv.tv_sec
            );
        }
    }
}