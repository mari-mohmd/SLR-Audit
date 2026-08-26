use std::time::{SystemTime, UNIX_EPOCH, Duration};

fn gen_rand_num() -> u64 {
    let sys_time = SystemTime::now().duration_since(UNIX_EPOCH).expect("error");
    let sys_time_sec = sys_time.as_secs().to_string();
    let rand_num_str = sys_time_sec.chars().last();
    return rand_num_str.expect("error").to_digit(10).expect("error").into();
}

fn main() {
    let mut x: u64 = 0;
    for i in 1..1000000000 {
        x += i + gen_rand_num();
    }
}