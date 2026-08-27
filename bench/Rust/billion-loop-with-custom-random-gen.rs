use std::io;

fn gen_rand_num(random_pool: &mut Vec<i32>) -> i32 {
    if let Some(rand_num) = random_pool.pop() {
        rand_num
    } else {
        *random_pool = vec![5, 4, 8, 9, 4, 2, 1];
        random_pool.pop().unwrap()
    }
}

fn compiled_function(random_pool: &mut Vec<i32>) -> i64 {
    let mut x: i64 = 0;

    for i in 0..1000000000 {
        let rand_num = gen_rand_num(random_pool);
        x += i + rand_num as i64;
    }
    x
}

fn main() {
    let mut random_pool: Vec<i32> = vec![5, 4, 8, 9, 4, 2, 1];
    let loop_value_num: i64 = 1000000000;
    let result = compiled_function(&mut random_pool);
}