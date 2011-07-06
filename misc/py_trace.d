#pragma D option quiet

self int depth;
self int last;

dtrace:::BEGIN
{
    printf("Tracing... Hit Ctrl-C to end.\n");
    printf(" %-70s %4s %10s : %s %s\n", "FILE", "LINE", "TIME",
           "FUNCTION NAME", "");
}

python*:::function-entry,
python*:::function-return
/ self->last == 0 /
{
    self->last = timestamp;
}

python*:::function-entry
/ dirname(copyinstr(arg0)) <= "/usr/lib/" /
{
    self->delta = (timestamp - self->last) / 1000;
    printf(" %-70s %4i %10i : %*s> %s\n", copyinstr(arg0), arg2, self->delta,
           self->depth, "", copyinstr(arg1));
    self-> depth++;
    self->last = timestamp;
}

python*:::function-return
/ dirname(copyinstr(arg0)) <= "/usr/lib/" /
{
    self->delta = (timestamp - self->last) / 1000;
    self->depth--;
    printf(" %-70s %4i %10i : %*s< %s\n", copyinstr(arg0), arg2, self->delta,
            self->depth, "", copyinstr(arg1));
    self->last = timestamp;
}
